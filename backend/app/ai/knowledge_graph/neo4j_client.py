import logging
from typing import Any, Dict, List, Optional
try:
    from neo4j import Driver, GraphDatabase, Result
except ImportError:
    Driver = Any  # type: ignore
    GraphDatabase = None  # type: ignore
    Result = Any  # type: ignore

from app.core.config import (
    NEO4J_DATABASE,
    NEO4J_PASSWORD,
    NEO4J_URI,
    NEO4J_USERNAME,
)

logger = logging.getLogger("careerverse.ai.knowledge_graph")


class Neo4jClient:
    """
    Manages persistent Neo4j Graph Database connections, query execution,
    and schema constraint lifecycle for candidate knowledge graph modeling.
    """

    def __init__(
        self,
        uri: str = NEO4J_URI,
        username: str = NEO4J_USERNAME,
        password: str = NEO4J_PASSWORD,
        database: str = NEO4J_DATABASE,
    ):
        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
        self._driver: Optional[Driver] = None
        self._available: Optional[bool] = None

    @property
    def driver(self) -> Driver:
        """Lazy initialization of the Neo4j driver."""
        if self._driver is None:
            if GraphDatabase is None:
                raise RuntimeError("neo4j package is not installed in the environment")
            logger.info("Initializing Neo4j driver at %s (database: %s)", self.uri, self.database)
            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password),
                connection_timeout=1.0,
                max_connection_lifetime=3600,
                max_connection_pool_size=50,
            )
        return self._driver

    def is_available(self) -> bool:
        """Checks whether the Neo4j server is actively reachable within 1s timeout."""
        if self._available is not None:
            return self._available
        try:
            self.driver.verify_connectivity()
            self._available = True
            logger.info("Neo4j connectivity successfully verified.")
        except Exception as exc:
            self._available = False
            logger.warning("Neo4j is not reachable at %s (%s); graph operations will run in-memory mode.", self.uri, exc)
        return self._available

    def verify_connectivity(self) -> bool:
        """Verifies active connectivity to the Neo4j instance."""
        try:
            self.driver.verify_connectivity()
            logger.info("Neo4j connectivity successfully verified.")
            return True
        except Exception as exc:
            logger.error("Failed to connect to Neo4j at %s: %s", self.uri, exc)
            raise

    def close(self):
        """Closes the Neo4j driver connection pool."""
        if self._driver is not None:
            self._driver.close()
            self._driver = None
            self._available = None
            logger.info("Neo4j driver connection closed.")

    def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Executes a read-only or transactional Cypher query and returns records as dictionaries.
        Returns an empty list on connection or execution error to prevent blocking AI pipelines.
        """
        if not self.is_available():
            return []
        try:
            db = database or self.database
            with self.driver.session(database=db) as session:
                result: Result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as exc:
            logger.warning("Neo4j execute_query error (%s); returning empty records", exc)
            return []

    def execute_write(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Executes a write transaction within a managed session.
        Returns an empty list if Neo4j is offline or fails to prevent blocking.
        """
        if not self.is_available():
            return []
        try:
            db = database or self.database

            def _tx_work(tx):
                res = tx.run(query, parameters or {})
                return [record.data() for record in res]

            with self.driver.session(database=db) as session:
                return session.execute_write(_tx_work)
        except Exception as exc:
            logger.warning("Neo4j execute_write error (%s); returning empty records", exc)
            return []

    def init_constraints(self):
        """
        Initializes uniqueness constraints and indexes on candidate knowledge graph nodes.
        Guarantees idempotency and query performance.
        """
        constraints = [
            # Candidate uniqueness by candidate_id
            """
            CREATE CONSTRAINT candidate_id_unique IF NOT EXISTS
            FOR (c:Candidate) REQUIRE c.candidate_id IS UNIQUE
            """,
            # Skill uniqueness by normalized skill name
            """
            CREATE CONSTRAINT skill_name_unique IF NOT EXISTS
            FOR (s:Skill) REQUIRE s.name IS UNIQUE
            """,
            # Project uniqueness by composite project_id
            """
            CREATE CONSTRAINT project_id_unique IF NOT EXISTS
            FOR (p:Project) REQUIRE p.project_id IS UNIQUE
            """,
            # Certification uniqueness by certification_id
            """
            CREATE CONSTRAINT certification_id_unique IF NOT EXISTS
            FOR (cert:Certification) REQUIRE cert.certification_id IS UNIQUE
            """,
            # Experience uniqueness by experience_id
            """
            CREATE CONSTRAINT experience_id_unique IF NOT EXISTS
            FOR (e:Experience) REQUIRE e.experience_id IS UNIQUE
            """,
            # Education uniqueness by education_id
            """
            CREATE CONSTRAINT education_id_unique IF NOT EXISTS
            FOR (edu:Education) REQUIRE edu.education_id IS UNIQUE
            """,
            # Technology uniqueness by name
            """
            CREATE CONSTRAINT technology_name_unique IF NOT EXISTS
            FOR (t:Technology) REQUIRE t.name IS UNIQUE
            """,
        ]

        with self.driver.session(database=self.database) as session:
            for constraint_cypher in constraints:
                try:
                    session.run(constraint_cypher)
                except Exception as exc:
                    logger.warning("Constraint creation warning (may already exist or not supported): %s", exc)

        logger.info("Neo4j constraints initialization complete.")


# Global Neo4j client singleton instance
neo4j_client = Neo4jClient()

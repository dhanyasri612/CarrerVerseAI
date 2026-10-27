import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { AIActivityProvider } from "./context/AIActivityContext";
import { ThemeProvider } from "./context/ThemeContext";

// New reimagined layout replaces the old sidebar Layout
import LayoutReimagined from "./components/LayoutReimagined";

// Pages
import LandingPage        from "./pages/LandingPage";
import LoginPage          from "./pages/LoginPage";
import RegisterPage       from "./pages/RegisterPage";
import DashboardReimagined from "./pages/DashboardReimagined";
import ResumePage         from "./pages/ResumePage";
import ProfilePage        from "./pages/ProfilePage";
import IntelligencePage   from "./pages/IntelligencePage";
import AIPage             from "./pages/AIPage";
import CareerQuizPage     from "./pages/CareerQuizPage";
import CareerDiscoveryPage from "./pages/CareerDiscoveryPage";
import SkillGapPage       from "./pages/SkillGapPage";
import LearningRoadmapPage from "./pages/LearningRoadmapPage";
import CareerIntelligencePage from "./pages/CareerIntelligencePage";
import InterviewPage      from "./pages/InterviewPage";
import DsaPracticePage    from "./pages/DsaPracticePage";
import TeachingStudioPage from "./pages/TeachingStudioPage";
import RepositoryLearningPage from "./pages/RepositoryLearningPage";
import CodingProfileLearningPage from "./pages/CodingProfileLearningPage";
import ResumeSkillLearningPage from "./pages/ResumeSkillLearningPage";
import QuestionBankPage from "./pages/QuestionBankPage";

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}
function PublicOnlyRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : children;
}

function App() {
  return (
    <ThemeProvider>
      <AIActivityProvider>
        <AuthProvider>
          <BrowserRouter>
            <Routes>
            {/* Public */}
            <Route path="/"        element={<LandingPage />} />
            <Route path="/login"   element={<PublicOnlyRoute><LoginPage /></PublicOnlyRoute>} />
            <Route path="/register" element={<PublicOnlyRoute><RegisterPage /></PublicOnlyRoute>} />

            {/* Dedicated Immersive Interview Room (Standalone Full-Screen View) */}
            <Route path="/ai/interview" element={<ProtectedRoute><InterviewPage /></ProtectedRoute>} />
            <Route path="/interview" element={<Navigate to="/ai/interview" replace />} />

            {/* Dedicated Teaching Sub-Pages */}
            <Route path="/teaching/repositories" element={<ProtectedRoute><RepositoryLearningPage /></ProtectedRoute>} />
            <Route path="/ai/teaching/repositories" element={<ProtectedRoute><RepositoryLearningPage /></ProtectedRoute>} />

            <Route path="/teaching/coding-profile" element={<ProtectedRoute><CodingProfileLearningPage /></ProtectedRoute>} />
            <Route path="/ai/teaching/coding-profile" element={<ProtectedRoute><CodingProfileLearningPage /></ProtectedRoute>} />

            <Route path="/teaching/resume-skills" element={<ProtectedRoute><ResumeSkillLearningPage /></ProtectedRoute>} />
            <Route path="/ai/teaching/resume-skills" element={<ProtectedRoute><ResumeSkillLearningPage /></ProtectedRoute>} />

            {/* Dedicated AI Teaching & Masterclass Room Entry Hub */}
            <Route path="/ai/teaching" element={<ProtectedRoute><TeachingStudioPage /></ProtectedRoute>} />
            <Route path="/ai/teaching-studio" element={<Navigate to="/ai/teaching" replace />} />
            <Route path="/teaching" element={<ProtectedRoute><TeachingStudioPage /></ProtectedRoute>} />

            {/* Protected — inside reimagined layout */}
            <Route element={<ProtectedRoute><LayoutReimagined /></ProtectedRoute>}>
              <Route path="/dashboard"      element={<DashboardReimagined />} />
              <Route path="/profile"        element={<ProfilePage />} />
              <Route path="/resume"         from="/resume" element={<ResumePage />} />
              <Route path="/career-discovery" element={<CareerDiscoveryPage />} />
              <Route path="/skill-gap"      element={<SkillGapPage />} />
              <Route path="/career-roadmap" element={<LearningRoadmapPage />} />
              <Route path="/career-quiz"    element={<CareerQuizPage />} />
              <Route path="/ai/intelligence" element={<CareerIntelligencePage />} />
              <Route path="/dsa-practice"   element={<DsaPracticePage />} />
              <Route path="/question-bank"  element={<QuestionBankPage />} />
              {/* Route aliases */}
              <Route path="/ai/question-bank"   element={<Navigate to="/question-bank" replace />} />
              <Route path="/questions"          element={<Navigate to="/question-bank" replace />} />
              <Route path="/dsa"                element={<Navigate to="/dsa-practice" replace />} />
              <Route path="/career-navigator"   element={<Navigate to="/career-discovery" replace />} />
              <Route path="/navigator"          element={<Navigate to="/career-discovery" replace />} />
              <Route path="/discovery"          element={<Navigate to="/career-discovery" replace />} />
              <Route path="/quiz"               element={<Navigate to="/career-quiz" replace />} />
              <Route path="/interview"          element={<Navigate to="/ai/interview" replace />} />
              <Route path="/roadmap"            element={<Navigate to="/career-roadmap" replace />} />
              {/* Legacy routes kept working */}
              <Route path="/resume-analysis"    element={<IntelligencePage mode="analysis" />} />
              <Route path="/recommendations"    element={<IntelligencePage mode="recommendations" />} />
              <Route path="/github"             element={<IntelligencePage mode="github" />} />
              <Route path="/resume-improvement" element={<IntelligencePage mode="improvement" />} />
              <Route path="/ai/recommend"       element={<AIPage mode="ai-recommend" />} />
              <Route path="/ai/skill-gap"       element={<AIPage mode="ai-skill-gap" />} />
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </AIActivityProvider>
    </ThemeProvider>
  );
}

export default App;

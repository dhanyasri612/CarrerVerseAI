import FeatureCard from './FeatureCard'
import './Features.css'

function Features() {
    return (
        <section className="features">
            <h2>Everything You Need For Your Career</h2>
            <div>
                <FeatureCard
                    title="Resume Analysis"
                    description="Get AI-powered insights from your resume."
                />
                <FeatureCard
                    title="Skill Gap Analysis"    
                    description="Discover the skills you need for your target role."
                />
                <FeatureCard
                    title="Career RoadMap"
                    description="Get a personalised roadmap for your career."
                />
            </div>
        </section>
    )
}
export default Features

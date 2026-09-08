import FeatureCard from './FeatureCard'
import './Features.css'

function Features() {
    const features = [
        {
            title:'Resume Analysis',
            description:'Get AI-powered insights from your resume.'
        },
        {
            title:'Skill Gap Analysis',
            description:'Discover the skills you need for your target role.'
        },
        {
            title:'Career RoadMap',
            description:'Get a personalised roadmap for your career.'
        }
    ]
    return (
        <section className="features">
            <h2>Everything You Need For Your Career</h2>
            <div>
                {features.map((feature) => (
                    <FeatureCard
                    key={feature.title}
                    title={feature.title}
                    description={feature.description}
                    />  
                ))}
            </div>
        </section>
    )
}
export default Features

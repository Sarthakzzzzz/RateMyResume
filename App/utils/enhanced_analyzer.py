try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-GUI backend for web
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False
import re
from .rating import *
import io
import base64

class EnhancedResumeAnalyzer:
    def __init__(self):
        self.job_requirements = {
            'software_engineer': {
                'required_skills': ['python', 'java', 'javascript', 'sql', 'git', 'algorithms', 'data structures'],
                'preferred_skills': ['react', 'node.js', 'aws', 'docker', 'kubernetes', 'mongodb', 'postgresql'],
                'experience_weight': 0.3,
                'skills_weight': 0.4,
                'education_weight': 0.2,
                'projects_weight': 0.1
            },
            'data_scientist': {
                'required_skills': ['python', 'r', 'sql', 'machine learning', 'statistics', 'pandas', 'numpy'],
                'preferred_skills': ['tensorflow', 'pytorch', 'scikit-learn', 'tableau', 'power bi', 'spark', 'hadoop'],
                'experience_weight': 0.25,
                'skills_weight': 0.45,
                'education_weight': 0.2,
                'projects_weight': 0.1
            },
            'product_manager': {
                'required_skills': ['product strategy', 'roadmap', 'stakeholder management', 'analytics', 'agile'],
                'preferred_skills': ['jira', 'confluence', 'sql', 'a/b testing', 'user research', 'wireframing'],
                'experience_weight': 0.4,
                'skills_weight': 0.25,
                'education_weight': 0.15,
                'projects_weight': 0.2
            },
            'marketing_manager': {
                'required_skills': ['digital marketing', 'seo', 'content marketing', 'analytics', 'campaign management'],
                'preferred_skills': ['google ads', 'facebook ads', 'hubspot', 'salesforce', 'photoshop', 'canva'],
                'experience_weight': 0.35,
                'skills_weight': 0.3,
                'education_weight': 0.15,
                'projects_weight': 0.2
            }
        }

    def analyze_for_position(self, resume_text: str, position: str = 'software_engineer') -> dict:
        """Comprehensive position-based resume analysis"""
        
        # Get base analysis
        base_analysis = calculate_resume_score(resume_text)
        
        # Position-specific analysis
        job_req = self.job_requirements.get(position, self.job_requirements['software_engineer'])
        
        # Skills matching
        skills_match = self._analyze_skills_match(resume_text, job_req)
        
        # Calculate position-specific score
        position_score = self._calculate_position_score(base_analysis, skills_match, job_req)
        
        # Generate improvement suggestions
        suggestions = self._generate_suggestions(base_analysis, skills_match, job_req, position)
        
        # Create comprehensive analysis
        analysis = {
            'base_analysis': base_analysis,
            'position': position,
            'position_score': position_score,
            'skills_analysis': skills_match,
            'suggestions': suggestions,
            'charts_data': self._prepare_charts_data(base_analysis, skills_match, position_score)
        }
        
        return analysis

    def _analyze_skills_match(self, resume_text: str, job_req: dict) -> dict:
        """Analyze how well resume skills match job requirements"""
        text_lower = resume_text.lower()
        
        required_found = []
        required_missing = []
        preferred_found = []
        preferred_missing = []
        
        for skill in job_req['required_skills']:
            if skill.lower() in text_lower:
                required_found.append(skill)
            else:
                required_missing.append(skill)
        
        for skill in job_req['preferred_skills']:
            if skill.lower() in text_lower:
                preferred_found.append(skill)
            else:
                preferred_missing.append(skill)
        
        return {
            'required_found': required_found,
            'required_missing': required_missing,
            'preferred_found': preferred_found,
            'preferred_missing': preferred_missing,
            'required_match_rate': len(required_found) / len(job_req['required_skills']) * 100,
            'preferred_match_rate': len(preferred_found) / len(job_req['preferred_skills']) * 100
        }

    def _calculate_position_score(self, base_analysis: dict, skills_match: dict, job_req: dict) -> dict:
        """Calculate position-specific weighted score"""
        
        # Normalize base scores to 0-100 scale
        experience_score = min(100, (base_analysis.get('experience_score', 0) / 10) * 100)
        education_score = min(100, (base_analysis.get('education_score', 0) / 8) * 100)
        projects_score = min(100, (base_analysis.get('project_score', 0) / 10) * 100)
        
        # Skills score based on matching
        skills_score = (skills_match['required_match_rate'] * 0.7 + 
                       skills_match['preferred_match_rate'] * 0.3)
        
        # Weighted final score
        weighted_score = (
            experience_score * job_req['experience_weight'] +
            skills_score * job_req['skills_weight'] +
            education_score * job_req['education_weight'] +
            projects_score * job_req['projects_weight']
        )
        
        return {
            'weighted_score': round(weighted_score, 1),
            'experience_score': round(experience_score, 1),
            'skills_score': round(skills_score, 1),
            'education_score': round(education_score, 1),
            'projects_score': round(projects_score, 1),
            'grade': self._get_grade(weighted_score)
        }

    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90: return 'A+'
        elif score >= 85: return 'A'
        elif score >= 80: return 'A-'
        elif score >= 75: return 'B+'
        elif score >= 70: return 'B'
        elif score >= 65: return 'B-'
        elif score >= 60: return 'C+'
        elif score >= 55: return 'C'
        elif score >= 50: return 'C-'
        else: return 'D'

    def _generate_suggestions(self, base_analysis: dict, skills_match: dict, job_req: dict, position: str) -> dict:
        """Generate automated improvement suggestions"""
        
        suggestions = {
            'critical': [],
            'important': [],
            'nice_to_have': []
        }
        
        # Critical suggestions
        if len(skills_match['required_missing']) > 0:
            suggestions['critical'].append({
                'category': 'Required Skills',
                'issue': f"Missing {len(skills_match['required_missing'])} required skills",
                'action': f"Add these skills: {', '.join(skills_match['required_missing'][:3])}",
                'impact': 'High'
            })
        
        if base_analysis.get('experience_score', 0) < 5:
            suggestions['critical'].append({
                'category': 'Experience',
                'issue': 'Insufficient work experience details',
                'action': 'Add more detailed work experience with quantified achievements',
                'impact': 'High'
            })
        
        # Important suggestions
        if len(skills_match['preferred_missing']) > 3:
            suggestions['important'].append({
                'category': 'Preferred Skills',
                'issue': f"Missing {len(skills_match['preferred_missing'])} preferred skills",
                'action': f"Consider adding: {', '.join(skills_match['preferred_missing'][:3])}",
                'impact': 'Medium'
            })
        
        if base_analysis.get('project_score', 0) < 5:
            suggestions['important'].append({
                'category': 'Projects',
                'issue': 'Limited project showcase',
                'action': 'Add 2-3 relevant projects with technical details and outcomes',
                'impact': 'Medium'
            })
        
        # Red flags as critical
        for flag in base_analysis.get('red_flags', []):
            suggestions['critical'].append({
                'category': 'Content Quality',
                'issue': flag,
                'action': 'Review and improve resume content',
                'impact': 'High'
            })
        
        # Nice to have suggestions
        if base_analysis.get('certifications_score', 0) < 3:
            suggestions['nice_to_have'].append({
                'category': 'Certifications',
                'issue': 'No relevant certifications',
                'action': f'Consider getting certifications relevant to {position}',
                'impact': 'Low'
            })
        
        return suggestions

    def _prepare_charts_data(self, base_analysis: dict, skills_match: dict, position_score: dict) -> dict:
        """Prepare data for chart generation"""
        
        # Score breakdown for pie chart
        score_breakdown = {
            'Experience': position_score['experience_score'],
            'Skills': position_score['skills_score'],
            'Education': position_score['education_score'],
            'Projects': position_score['projects_score']
        }
        
        # Skills matching data
        skills_data = {
            'Required Skills Found': len(skills_match['required_found']),
            'Required Skills Missing': len(skills_match['required_missing']),
            'Preferred Skills Found': len(skills_match['preferred_found']),
            'Preferred Skills Missing': len(skills_match['preferred_missing'])
        }
        
        # Section scores for bar chart
        section_scores = {
            'Personal Info': base_analysis.get('personal_info_score', 0),
            'Experience': base_analysis.get('experience_score', 0),
            'Projects': base_analysis.get('project_score', 0),
            'Education': base_analysis.get('education_score', 0),
            'Skills': base_analysis.get('tech_skills_score', 0),
            'Achievements': base_analysis.get('achievements_score', 0),
            'Certifications': base_analysis.get('certifications_score', 0)
        }
        
        return {
            'score_breakdown': score_breakdown,
            'skills_data': skills_data,
            'section_scores': section_scores,
            'overall_score': position_score['weighted_score']
        }

    def generate_charts(self, charts_data: dict) -> dict:
        """Generate all visualization charts"""
        
        if not CHARTS_AVAILABLE:
            return {key: "" for key in ['gauge', 'pie', 'skills_bar', 'radar', 'sections_bar']}
        
        try:
            plt.style.use('seaborn-v0_8')
        except:
            pass
        charts = {}
        
        # 1. Overall Score Gauge Chart
        charts['gauge'] = self._create_gauge_chart(charts_data['overall_score'])
        
        # 2. Score Breakdown Pie Chart
        charts['pie'] = self._create_pie_chart(charts_data['score_breakdown'])
        
        # 3. Skills Analysis Bar Chart
        charts['skills_bar'] = self._create_skills_bar_chart(charts_data['skills_data'])
        
        # 4. Section Scores Radar Chart
        charts['radar'] = self._create_radar_chart(charts_data['section_scores'])
        
        # 5. Detailed Section Scores Bar Chart
        charts['sections_bar'] = self._create_sections_bar_chart(charts_data['section_scores'])
        
        return charts

    def _create_gauge_chart(self, score: float) -> str:
        """Create gauge chart for overall score"""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Create gauge
        theta = np.linspace(0, np.pi, 100)
        r = 1
        
        # Background arc
        ax.plot(r * np.cos(theta), r * np.sin(theta), 'lightgray', linewidth=20)
        
        # Score arc
        score_theta = np.linspace(0, np.pi * (score / 100), int(score))
        color = 'red' if score < 50 else 'orange' if score < 75 else 'green'
        ax.plot(r * np.cos(score_theta), r * np.sin(score_theta), color, linewidth=20)
        
        # Score text
        ax.text(0, -0.3, f'{score:.1f}%', ha='center', va='center', fontsize=24, fontweight='bold')
        ax.text(0, -0.5, 'Overall Score', ha='center', va='center', fontsize=14)
        
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-0.7, 1.2)
        ax.set_aspect('equal')
        ax.axis('off')
        plt.title('Resume Score', fontsize=16, fontweight='bold', pad=20)
        
        return self._fig_to_base64(fig)

    def _create_pie_chart(self, data: dict) -> str:
        """Create pie chart for score breakdown"""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        wedges, texts, autotexts = ax.pie(data.values(), labels=data.keys(), autopct='%1.1f%%',
                                         colors=colors, startangle=90)
        
        plt.title('Score Breakdown by Category', fontsize=14, fontweight='bold')
        return self._fig_to_base64(fig)

    def _create_skills_bar_chart(self, data: dict) -> str:
        """Create bar chart for skills analysis"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        categories = list(data.keys())
        values = list(data.values())
        colors = ['green', 'red', 'lightgreen', 'lightcoral']
        
        bars = ax.bar(categories, values, color=colors)
        ax.set_ylabel('Count')
        ax.set_title('Skills Analysis', fontsize=14, fontweight='bold')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom')
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        return self._fig_to_base64(fig)

    def _create_radar_chart(self, data: dict) -> str:
        """Create radar chart for section scores"""
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        
        categories = list(data.keys())
        values = list(data.values())
        
        # Normalize values to 0-10 scale for better visualization
        max_val = max(values) if max(values) > 0 else 1
        normalized_values = [v / max_val * 10 for v in values]
        
        # Add first value at end to close the circle
        normalized_values += normalized_values[:1]
        
        # Calculate angles
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]
        
        # Plot
        ax.plot(angles, normalized_values, 'o-', linewidth=2, color='#4ECDC4')
        ax.fill(angles, normalized_values, alpha=0.25, color='#4ECDC4')
        
        # Add labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 10)
        
        plt.title('Resume Sections Analysis', size=14, fontweight='bold', pad=20)
        return self._fig_to_base64(fig)

    def _create_sections_bar_chart(self, data: dict) -> str:
        """Create horizontal bar chart for section scores"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        sections = list(data.keys())
        scores = list(data.values())
        
        # Create color map based on scores
        colors = ['red' if s < 3 else 'orange' if s < 6 else 'green' for s in scores]
        
        bars = ax.barh(sections, scores, color=colors)
        ax.set_xlabel('Score')
        ax.set_title('Detailed Section Scores', fontsize=14, fontweight='bold')
        
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                   f'{scores[i]:.1f}', ha='left', va='center')
        
        plt.tight_layout()
        return self._fig_to_base64(fig)

    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string"""
        if not CHARTS_AVAILABLE:
            return ""
        import io
        import base64
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        return image_base64

    def generate_report(self, analysis: dict) -> str:
        """Generate comprehensive HTML report"""
        
        charts = self.generate_charts(analysis['charts_data'])
        
        html_report = f"""
        <div class="resume-analysis-report">
            <h1>Resume Analysis Report</h1>
            
            <div class="summary-section">
                <h2>Overall Assessment</h2>
                <div class="score-display">
                    <div class="main-score">
                        <span class="score-number">{analysis['position_score']['weighted_score']:.1f}%</span>
                        <span class="score-grade">Grade: {analysis['position_score']['grade']}</span>
                    </div>
                    <p>Position: <strong>{analysis['position'].replace('_', ' ').title()}</strong></p>
                </div>
            </div>
            
            <div class="charts-section">
                <div class="chart-container">
                    <img src="data:image/png;base64,{charts['gauge']}" alt="Overall Score Gauge">
                </div>
                <div class="chart-container">
                    <img src="data:image/png;base64,{charts['pie']}" alt="Score Breakdown">
                </div>
            </div>
            
            <div class="skills-analysis">
                <h2>Skills Analysis</h2>
                <div class="skills-stats">
                    <div class="skill-stat">
                        <span class="stat-number">{len(analysis['skills_analysis']['required_found'])}</span>
                        <span class="stat-label">Required Skills Found</span>
                    </div>
                    <div class="skill-stat">
                        <span class="stat-number">{len(analysis['skills_analysis']['required_missing'])}</span>
                        <span class="stat-label">Required Skills Missing</span>
                    </div>
                </div>
                <img src="data:image/png;base64,{charts['skills_bar']}" alt="Skills Analysis">
            </div>
            
            <div class="suggestions-section">
                <h2>Improvement Suggestions</h2>
                {self._format_suggestions_html(analysis['suggestions'])}
            </div>
            
            <div class="detailed-charts">
                <img src="data:image/png;base64,{charts['radar']}" alt="Radar Chart">
                <img src="data:image/png;base64,{charts['sections_bar']}" alt="Section Scores">
            </div>
        </div>
        """
        
        return html_report

    def _format_suggestions_html(self, suggestions: dict) -> str:
        """Format suggestions as HTML"""
        html = ""
        
        for priority, items in suggestions.items():
            if items:
                html += f"<h3>{priority.replace('_', ' ').title()} Priority</h3><ul>"
                for item in items:
                    html += f"""
                    <li class="suggestion-item {priority}">
                        <strong>{item['category']}:</strong> {item['issue']}<br>
                        <em>Action:</em> {item['action']}<br>
                        <span class="impact">Impact: {item['impact']}</span>
                    </li>
                    """
                html += "</ul>"
        
        return html
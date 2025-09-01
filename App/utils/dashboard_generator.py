try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    import numpy as np
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False
# from wordcloud import WordCloud  # Removed due to installation issues
import io
import base64
from .enhanced_analyzer import EnhancedResumeAnalyzer

class ResumeDashboard:
    def __init__(self):
        self.analyzer = EnhancedResumeAnalyzer()
        if CHARTS_AVAILABLE:
            try:
                import matplotlib
                matplotlib.use('Agg')  # Use non-GUI backend
                plt.style.use('seaborn-v0_8')
            except:
                pass
        
    def generate_comprehensive_dashboard(self, resume_text: str, position: str = 'software_engineer') -> dict:
        """Generate a comprehensive dashboard with all analytics"""
        
        # Get analysis
        analysis = self.analyzer.analyze_for_position(resume_text, position)
        
        if not CHARTS_AVAILABLE:
            return {
                'analysis': analysis,
                'charts': {key: "" for key in ['score_gauge', 'skills_radar', 'improvement_priority', 
                          'section_comparison', 'skills_heatmap', 'wordcloud', 'progress_bars', 'recommendation_chart']}
            }
        
        # Generate all charts
        dashboard_data = {
            'analysis': analysis,
            'charts': {
                'score_gauge': self._create_advanced_gauge(analysis['position_score']['weighted_score']),
                'skills_radar': self._create_skills_radar(analysis),
                'improvement_priority': self._create_improvement_priority_chart(analysis['suggestions']),
                'section_comparison': self._create_section_comparison(analysis['base_analysis']),
                'skills_heatmap': self._create_skills_heatmap(analysis['skills_analysis']),
                'wordcloud': self._create_resume_wordcloud(resume_text),
                'progress_bars': self._create_progress_bars(analysis['position_score']),
                'recommendation_chart': self._create_recommendation_chart(analysis)
            }
        }
        
        return dashboard_data
    
    def _create_advanced_gauge(self, score: float) -> str:
        """Create an advanced gauge chart with color zones"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create gauge background
        theta = np.linspace(0, np.pi, 100)
        
        # Color zones
        zones = [
            (0, 50, '#e74c3c', 'Needs Improvement'),
            (50, 70, '#f39c12', 'Good'),
            (70, 85, '#3498db', 'Very Good'),
            (85, 100, '#27ae60', 'Excellent')
        ]
        
        for start, end, color, label in zones:
            zone_theta = np.linspace(np.pi * (1 - end/100), np.pi * (1 - start/100), 50)
            ax.plot(np.cos(zone_theta), np.sin(zone_theta), color=color, linewidth=15, alpha=0.3)
        
        # Score needle
        score_angle = np.pi * (1 - score/100)
        needle_x = [0, 0.8 * np.cos(score_angle)]
        needle_y = [0, 0.8 * np.sin(score_angle)]
        ax.plot(needle_x, needle_y, 'black', linewidth=4)
        ax.plot(0, 0, 'ko', markersize=10)
        
        # Score text
        ax.text(0, -0.3, f'{score:.1f}%', ha='center', va='center', 
                fontsize=28, fontweight='bold')
        ax.text(0, -0.45, 'Resume Score', ha='center', va='center', 
                fontsize=16, color='gray')
        
        # Zone labels
        ax.text(-0.7, 0.7, 'Needs\nImprovement', ha='center', va='center', 
                fontsize=10, color='#e74c3c', fontweight='bold')
        ax.text(0.7, 0.7, 'Excellent', ha='center', va='center', 
                fontsize=10, color='#27ae60', fontweight='bold')
        
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-0.6, 1.2)
        ax.set_aspect('equal')
        ax.axis('off')
        plt.title('Overall Resume Assessment', fontsize=18, fontweight='bold', pad=20)
        
        return self._fig_to_base64(fig)
    
    def _create_skills_radar(self, analysis: dict) -> str:
        """Create radar chart for skills analysis"""
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # Data preparation
        categories = ['Technical Skills', 'Experience', 'Education', 'Projects', 
                     'Certifications', 'Leadership', 'Communication']
        
        base = analysis['base_analysis']
        values = [
            min(10, base.get('tech_skills_score', 0)),
            min(10, base.get('experience_score', 0)),
            min(10, base.get('education_score', 0)),
            min(10, base.get('project_score', 0)),
            min(10, base.get('certifications_score', 0)),
            min(10, base.get('leadership_score', 0)),
            10 - len(base.get('red_flags', []))  # Communication proxy
        ]
        
        # Normalize to 0-10 scale
        values = [max(0, v) for v in values]
        values += values[:1]  # Close the circle
        
        # Calculate angles
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]
        
        # Plot
        ax.plot(angles, values, 'o-', linewidth=3, color='#3498db', markersize=8)
        ax.fill(angles, values, alpha=0.25, color='#3498db')
        
        # Customize
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=12)
        ax.set_ylim(0, 10)
        ax.set_yticks(range(0, 11, 2))
        ax.set_yticklabels(range(0, 11, 2), fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.title('Skills & Competencies Radar', size=16, fontweight='bold', pad=30)
        
        return self._fig_to_base64(fig)
    
    def _create_improvement_priority_chart(self, suggestions: dict) -> str:
        """Create priority chart for improvements"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Count suggestions by priority and category
        priority_data = {}
        categories = set()
        
        for priority, items in suggestions.items():
            priority_data[priority] = {}
            for item in items:
                category = item['category']
                categories.add(category)
                priority_data[priority][category] = priority_data[priority].get(category, 0) + 1
        
        # Create stacked bar chart
        categories = list(categories)
        priorities = ['critical', 'important', 'nice_to_have']
        colors = ['#e74c3c', '#f39c12', '#3498db']
        
        bottom = np.zeros(len(categories))
        
        for i, priority in enumerate(priorities):
            values = [priority_data.get(priority, {}).get(cat, 0) for cat in categories]
            ax.bar(categories, values, bottom=bottom, label=priority.replace('_', ' ').title(), 
                   color=colors[i], alpha=0.8)
            bottom += values
        
        ax.set_ylabel('Number of Suggestions')
        ax.set_title('Improvement Priorities by Category', fontsize=16, fontweight='bold')
        ax.legend()
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        return self._fig_to_base64(fig)
    
    def _create_section_comparison(self, base_analysis: dict) -> str:
        """Create section comparison chart"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Current scores
        sections = {
            'Personal Info': base_analysis.get('personal_info_score', 0),
            'Experience': base_analysis.get('experience_score', 0),
            'Projects': base_analysis.get('project_score', 0),
            'Education': base_analysis.get('education_score', 0),
            'Skills': base_analysis.get('tech_skills_score', 0),
            'Achievements': base_analysis.get('achievements_score', 0),
            'Certifications': base_analysis.get('certifications_score', 0)
        }
        
        # Ideal scores (what companies typically look for)
        ideal_scores = {
            'Personal Info': 10,
            'Experience': 15,
            'Projects': 10,
            'Education': 8,
            'Skills': 20,
            'Achievements': 8,
            'Certifications': 6
        }
        
        # Current vs Ideal
        x = range(len(sections))
        current = list(sections.values())
        ideal = list(ideal_scores.values())
        
        ax1.bar([i - 0.2 for i in x], current, 0.4, label='Current', color='#3498db', alpha=0.7)
        ax1.bar([i + 0.2 for i in x], ideal, 0.4, label='Industry Standard', color='#27ae60', alpha=0.7)
        
        ax1.set_xlabel('Resume Sections')
        ax1.set_ylabel('Score')
        ax1.set_title('Current vs Industry Standard')
        ax1.set_xticks(x)
        ax1.set_xticklabels(sections.keys(), rotation=45, ha='right')
        ax1.legend()
        
        # Gap analysis
        gaps = [ideal[i] - current[i] for i in range(len(current))]
        colors = ['red' if gap > 0 else 'green' for gap in gaps]
        
        ax2.barh(list(sections.keys()), gaps, color=colors, alpha=0.7)
        ax2.set_xlabel('Score Gap (Negative = Above Standard)')
        ax2.set_title('Improvement Gaps')
        ax2.axvline(x=0, color='black', linestyle='-', alpha=0.3)
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def _create_skills_heatmap(self, skills_analysis: dict) -> str:
        """Create skills matching heatmap"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Create data matrix
        data = {
            'Required Skills': [
                len(skills_analysis['required_found']),
                len(skills_analysis['required_missing'])
            ],
            'Preferred Skills': [
                len(skills_analysis['preferred_found']),
                len(skills_analysis['preferred_missing'])
            ]
        }
        
        df = pd.DataFrame(data, index=['Found', 'Missing'])
        
        # Create heatmap
        sns.heatmap(df, annot=True, fmt='d', cmap='RdYlGn', 
                   cbar_kws={'label': 'Count'}, ax=ax)
        
        ax.set_title('Skills Matching Analysis', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        return self._fig_to_base64(fig)
    
    def _create_resume_wordcloud(self, resume_text: str) -> str:
        """Create simple keyword visualization"""
        import re
        from collections import Counter
        
        # Extract keywords
        words = re.findall(r'\b[a-zA-Z]{3,}\b', resume_text.lower())
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an', 'is', 'are', 'was', 'were'}
        keywords = [w for w in words if w not in stop_words]
        top_words = Counter(keywords).most_common(15)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if top_words:
            words, counts = zip(*top_words)
            y_pos = range(len(words))
            
            bars = ax.barh(y_pos, counts, color='skyblue', alpha=0.7)
            ax.set_yticks(y_pos)
            ax.set_yticklabels(words)
            ax.set_xlabel('Frequency')
            ax.set_title('Top Resume Keywords', fontsize=16, fontweight='bold')
            
            # Add count labels
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                       str(counts[i]), ha='left', va='center')
        else:
            ax.text(0.5, 0.5, 'No Keywords\nFound', ha='center', va='center', 
                   fontsize=20, color='gray')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
        
        ax.axis('off') if not top_words else None
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def _create_progress_bars(self, position_score: dict) -> str:
        """Create progress bars for different score components"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        categories = ['Experience', 'Skills', 'Education', 'Projects']
        scores = [
            position_score['experience_score'],
            position_score['skills_score'],
            position_score['education_score'],
            position_score['projects_score']
        ]
        
        # Create horizontal progress bars
        y_pos = np.arange(len(categories))
        
        # Background bars
        ax.barh(y_pos, [100] * len(categories), color='lightgray', alpha=0.3)
        
        # Progress bars with color coding
        colors = ['#e74c3c' if s < 50 else '#f39c12' if s < 75 else '#27ae60' for s in scores]
        bars = ax.barh(y_pos, scores, color=colors, alpha=0.8)
        
        # Add percentage labels
        for i, (bar, score) in enumerate(zip(bars, scores)):
            ax.text(score + 2, bar.get_y() + bar.get_height()/2, 
                   f'{score:.1f}%', va='center', fontweight='bold')
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(categories)
        ax.set_xlabel('Score Percentage')
        ax.set_title('Score Breakdown by Category', fontsize=16, fontweight='bold')
        ax.set_xlim(0, 105)
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def _create_recommendation_chart(self, analysis: dict) -> str:
        """Create recommendation priority chart"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Extract recommendation data
        suggestions = analysis['suggestions']
        all_suggestions = []
        
        for priority, items in suggestions.items():
            for item in items:
                all_suggestions.append({
                    'category': item['category'],
                    'priority': priority,
                    'impact': item['impact']
                })
        
        if not all_suggestions:
            ax.text(0.5, 0.5, 'No specific recommendations\nYour resume looks good!', 
                   ha='center', va='center', fontsize=16, color='green', fontweight='bold')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            return self._fig_to_base64(fig)
        
        # Create bubble chart
        df = pd.DataFrame(all_suggestions)
        
        priority_map = {'critical': 3, 'important': 2, 'nice_to_have': 1}
        impact_map = {'High': 3, 'Medium': 2, 'Low': 1}
        
        df['priority_num'] = df['priority'].map(priority_map)
        df['impact_num'] = df['impact'].map(impact_map)
        
        # Group by category
        grouped = df.groupby('category').agg({
            'priority_num': 'mean',
            'impact_num': 'mean'
        }).reset_index()
        
        # Create scatter plot
        scatter = ax.scatter(grouped['priority_num'], grouped['impact_num'], 
                           s=200, alpha=0.6, c=range(len(grouped)), cmap='viridis')
        
        # Add labels
        for i, row in grouped.iterrows():
            ax.annotate(row['category'], (row['priority_num'], row['impact_num']), 
                       xytext=(5, 5), textcoords='offset points', fontsize=10)
        
        ax.set_xlabel('Priority Level')
        ax.set_ylabel('Impact Level')
        ax.set_title('Improvement Recommendations Matrix', fontsize=16, fontweight='bold')
        ax.set_xticks([1, 2, 3])
        ax.set_xticklabels(['Nice to Have', 'Important', 'Critical'])
        ax.set_yticks([1, 2, 3])
        ax.set_yticklabels(['Low Impact', 'Medium Impact', 'High Impact'])
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string"""
        if not CHARTS_AVAILABLE:
            return ""
        import io
        import base64
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', bbox_inches='tight', dpi=150, facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        return image_base64
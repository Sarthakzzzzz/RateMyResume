import re
import spacy
from collections import Counter
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    import math

class AdvancedResumeAnalyzer:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        
        # Industry-specific skill databases
        self.skill_databases = {
            'software_engineer': {
                'core_skills': ['python', 'java', 'javascript', 'c++', 'sql', 'git', 'algorithms', 'data structures'],
                'frameworks': ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'node.js', 'express'],
                'tools': ['docker', 'kubernetes', 'jenkins', 'aws', 'azure', 'gcp', 'mongodb', 'postgresql'],
                'methodologies': ['agile', 'scrum', 'devops', 'ci/cd', 'tdd', 'microservices'],
                'experience_keywords': ['developed', 'built', 'implemented', 'designed', 'optimized', 'scaled', 'deployed']
            },
            'data_scientist': {
                'core_skills': ['python', 'r', 'sql', 'statistics', 'machine learning', 'deep learning'],
                'frameworks': ['pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras'],
                'tools': ['jupyter', 'tableau', 'power bi', 'spark', 'hadoop', 'aws', 'docker'],
                'methodologies': ['data mining', 'feature engineering', 'model validation', 'a/b testing'],
                'experience_keywords': ['analyzed', 'modeled', 'predicted', 'visualized', 'extracted', 'processed']
            },
            'product_manager': {
                'core_skills': ['product strategy', 'roadmap', 'stakeholder management', 'user research', 'analytics'],
                'frameworks': ['agile', 'scrum', 'lean', 'design thinking', 'user stories'],
                'tools': ['jira', 'confluence', 'figma', 'mixpanel', 'google analytics', 'sql'],
                'methodologies': ['market research', 'competitive analysis', 'go-to-market', 'product launch'],
                'experience_keywords': ['launched', 'managed', 'coordinated', 'prioritized', 'defined', 'executed']
            },
            'marketing_manager': {
                'core_skills': ['digital marketing', 'seo', 'sem', 'content marketing', 'social media', 'analytics'],
                'frameworks': ['marketing automation', 'lead generation', 'conversion optimization', 'brand management'],
                'tools': ['google ads', 'facebook ads', 'hubspot', 'salesforce', 'mailchimp', 'hootsuite'],
                'methodologies': ['campaign management', 'market segmentation', 'customer acquisition', 'retention'],
                'experience_keywords': ['increased', 'grew', 'generated', 'optimized', 'managed', 'executed']
            }
        }
        
        # ATS-friendly keywords
        self.ats_keywords = {
            'action_verbs': ['achieved', 'administered', 'analyzed', 'built', 'collaborated', 'created', 
                           'delivered', 'developed', 'executed', 'implemented', 'improved', 'increased',
                           'led', 'managed', 'optimized', 'organized', 'reduced', 'resolved', 'streamlined'],
            'quantifiers': [r'\d+%', r'\$\d+', r'\d+\s*(million|thousand|k|m)', r'\d+\s*(users|customers|clients)',
                          r'\d+\s*(projects|teams|people)', r'\d+\s*(years|months)', r'\d+x\s*improvement']
        }

    def advanced_skill_extraction(self, resume_text: str, position: str) -> dict:
        """Advanced skill extraction using NLP and fuzzy matching"""
        text_lower = resume_text.lower()
        doc = self.nlp(resume_text)
        
        position_skills = self.skill_databases.get(position, self.skill_databases['software_engineer'])
        
        # Extract skills with context scoring
        found_skills = {category: [] for category in position_skills.keys()}
        skill_scores = {}
        
        for category, skills in position_skills.items():
            for skill in skills:
                # Exact match
                if skill in text_lower:
                    found_skills[category].append(skill)
                    # Context scoring - higher score if skill appears in experience/projects section
                    context_score = self._calculate_context_score(resume_text, skill)
                    skill_scores[skill] = context_score
                
                # Fuzzy matching for variations
                variations = self._get_skill_variations(skill)
                for variation in variations:
                    if variation in text_lower and variation not in found_skills[category]:
                        found_skills[category].append(variation)
                        skill_scores[variation] = self._calculate_context_score(resume_text, variation)
        
        return {
            'found_skills': found_skills,
            'skill_scores': skill_scores,
            'total_skills': sum(len(skills) for skills in found_skills.values())
        }

    def _calculate_context_score(self, resume_text: str, skill: str) -> float:
        """Calculate skill relevance based on context"""
        lines = resume_text.lower().split('\n')
        score = 1.0
        
        for i, line in enumerate(lines):
            if skill in line:
                # Higher score if in experience/project sections
                if any(keyword in line for keyword in ['experience', 'project', 'work', 'job']):
                    score += 0.5
                # Higher score if mentioned with action verbs
                if any(verb in line for verb in self.ats_keywords['action_verbs']):
                    score += 0.3
                # Higher score if mentioned with quantifiers
                if any(re.search(pattern, line) for pattern in self.ats_keywords['quantifiers']):
                    score += 0.4
        
        return min(score, 3.0)  # Cap at 3.0

    def _get_skill_variations(self, skill: str) -> list:
        """Get common variations of a skill"""
        variations = {
            'javascript': ['js', 'node.js', 'nodejs'],
            'python': ['py'],
            'machine learning': ['ml', 'artificial intelligence', 'ai'],
            'tensorflow': ['tf'],
            'postgresql': ['postgres'],
            'mongodb': ['mongo'],
            'amazon web services': ['aws'],
            'google cloud platform': ['gcp'],
            'microsoft azure': ['azure']
        }
        return variations.get(skill, [])

    def calculate_ats_score(self, resume_text: str) -> dict:
        """Calculate ATS (Applicant Tracking System) compatibility score"""
        score = 0
        details = {}
        
        # 1. Action verbs usage
        action_verb_count = sum(1 for verb in self.ats_keywords['action_verbs'] 
                               if verb in resume_text.lower())
        action_score = min(action_verb_count * 2, 20)
        score += action_score
        details['action_verbs'] = {'count': action_verb_count, 'score': action_score}
        
        # 2. Quantified achievements
        quantifier_count = sum(1 for pattern in self.ats_keywords['quantifiers'] 
                              if re.search(pattern, resume_text, re.IGNORECASE))
        quant_score = min(quantifier_count * 5, 25)
        score += quant_score
        details['quantified_achievements'] = {'count': quantifier_count, 'score': quant_score}
        
        # 3. Section structure
        sections = ['experience', 'education', 'skills', 'projects']
        section_count = sum(1 for section in sections if section in resume_text.lower())
        section_score = section_count * 5
        score += section_score
        details['sections'] = {'found': section_count, 'score': section_score}
        
        # 4. Length optimization (300-800 words ideal)
        word_count = len(resume_text.split())
        if 300 <= word_count <= 800:
            length_score = 15
        elif 200 <= word_count < 300 or 800 < word_count <= 1000:
            length_score = 10
        else:
            length_score = 5
        score += length_score
        details['length'] = {'word_count': word_count, 'score': length_score}
        
        # 5. Contact information completeness
        email = bool(re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', resume_text))
        phone = bool(re.search(r'\+?[\d\s\-\(\)]{10,}', resume_text))
        contact_score = (email + phone) * 5
        score += contact_score
        details['contact_info'] = {'email': email, 'phone': phone, 'score': contact_score}
        
        return {
            'total_score': min(score, 100),
            'details': details,
            'grade': self._get_ats_grade(score)
        }

    def _get_ats_grade(self, score: float) -> str:
        """Convert ATS score to grade"""
        if score >= 85: return 'Excellent'
        elif score >= 70: return 'Good'
        elif score >= 55: return 'Fair'
        else: return 'Needs Improvement'

    def semantic_job_matching(self, resume_text: str, position: str) -> dict:
        """Use semantic similarity to match resume with job requirements"""
        
        if not ML_AVAILABLE:
            # Fallback keyword matching
            position_skills = self.skill_databases.get(position, self.skill_databases['software_engineer'])
            all_required_skills = []
            for skills in position_skills.values():
                all_required_skills.extend(skills)
            
            found_skills = [skill for skill in all_required_skills if skill in resume_text.lower()]
            similarity_score = (len(found_skills) / len(all_required_skills)) * 100 if all_required_skills else 50
            
            return {
                'similarity_score': similarity_score,
                'matching_terms': found_skills[:10],
                'match_grade': self._get_match_grade(similarity_score)
            }
        
        # Job requirement templates
        job_templates = {
            'software_engineer': """
            Software Engineer with experience in programming languages like Python, Java, JavaScript.
            Experience with frameworks like React, Django, Spring. Knowledge of databases, cloud platforms,
            version control systems. Strong problem-solving skills and experience with agile methodologies.
            """,
            'data_scientist': """
            Data Scientist with expertise in Python, R, machine learning, statistics, data analysis.
            Experience with pandas, numpy, scikit-learn, TensorFlow. Knowledge of data visualization,
            SQL databases, big data technologies. Strong analytical and mathematical skills.
            """,
            'product_manager': """
            Product Manager with experience in product strategy, roadmap planning, stakeholder management.
            Knowledge of agile methodologies, user research, analytics tools. Strong communication and
            leadership skills. Experience with product launches and go-to-market strategies.
            """,
            'marketing_manager': """
            Marketing Manager with expertise in digital marketing, SEO, content marketing, social media.
            Experience with marketing automation tools, analytics platforms, campaign management.
            Strong creative and analytical skills with focus on customer acquisition and retention.
            """
        }
        
        job_description = job_templates.get(position, job_templates['software_engineer'])
        
        try:
            # Create TF-IDF vectors
            vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
            
            # Calculate cosine similarity
            similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # Get top matching terms
            feature_names = vectorizer.get_feature_names_out()
            resume_vector = tfidf_matrix[0].toarray()[0]
            job_vector = tfidf_matrix[1].toarray()[0]
            
            # Find common important terms
            common_terms = []
            for i, (resume_score, job_score) in enumerate(zip(resume_vector, job_vector)):
                if resume_score > 0 and job_score > 0:
                    common_terms.append((feature_names[i], resume_score * job_score))
            
            # Sort by relevance
            common_terms.sort(key=lambda x: x[1], reverse=True)
            top_matches = [term[0] for term in common_terms[:10]]
            
        except Exception:
            similarity_score = 0.5
            top_matches = []
        
        return {
            'similarity_score': similarity_score * 100,
            'matching_terms': top_matches,
            'match_grade': self._get_match_grade(similarity_score * 100)
        }

    def _get_match_grade(self, score: float) -> str:
        """Convert similarity score to match grade"""
        if score >= 80: return 'Excellent Match'
        elif score >= 65: return 'Good Match'
        elif score >= 50: return 'Fair Match'
        else: return 'Poor Match'

    def comprehensive_analysis(self, resume_text: str, position: str) -> dict:
        """Perform comprehensive resume analysis"""
        
        # 1. Advanced skill analysis
        skill_analysis = self.advanced_skill_extraction(resume_text, position)
        
        # 2. ATS compatibility
        ats_analysis = self.calculate_ats_score(resume_text)
        
        # 3. Semantic job matching
        semantic_analysis = self.semantic_job_matching(resume_text, position)
        
        # 4. Experience quality analysis
        experience_analysis = self._analyze_experience_quality(resume_text)
        
        # 5. Calculate weighted final score
        final_score = self._calculate_weighted_score(
            skill_analysis, ats_analysis, semantic_analysis, experience_analysis, position
        )
        
        return {
            'skill_analysis': skill_analysis,
            'ats_analysis': ats_analysis,
            'semantic_analysis': semantic_analysis,
            'experience_analysis': experience_analysis,
            'final_score': final_score,
            'recommendations': self._generate_precise_recommendations(
                skill_analysis, ats_analysis, semantic_analysis, position
            )
        }

    def _analyze_experience_quality(self, resume_text: str) -> dict:
        """Analyze quality and relevance of experience descriptions"""
        doc = self.nlp(resume_text)
        
        # Extract experience-related sentences
        experience_sentences = []
        for sent in doc.sents:
            if any(keyword in sent.text.lower() for keyword in 
                  ['experience', 'worked', 'developed', 'managed', 'led', 'built']):
                experience_sentences.append(sent.text)
        
        # Quality metrics
        quality_score = 0
        details = {}
        
        # 1. Action verb usage in experience
        action_verbs_used = []
        for sent in experience_sentences:
            for verb in self.ats_keywords['action_verbs']:
                if verb in sent.lower():
                    action_verbs_used.append(verb)
        
        action_diversity = len(set(action_verbs_used))
        quality_score += min(action_diversity * 3, 30)
        details['action_verb_diversity'] = action_diversity
        
        # 2. Quantified results
        quantified_results = 0
        for sent in experience_sentences:
            for pattern in self.ats_keywords['quantifiers']:
                if re.search(pattern, sent, re.IGNORECASE):
                    quantified_results += 1
        
        quality_score += min(quantified_results * 5, 25)
        details['quantified_results'] = quantified_results
        
        # 3. Technical depth (technical terms per sentence)
        technical_terms = ['api', 'database', 'framework', 'algorithm', 'optimization', 
                          'integration', 'architecture', 'scalability', 'performance']
        tech_mentions = sum(1 for sent in experience_sentences 
                           for term in technical_terms if term in sent.lower())
        
        quality_score += min(tech_mentions * 2, 20)
        details['technical_depth'] = tech_mentions
        
        # 4. Experience length and detail
        if ML_AVAILABLE:
            avg_sentence_length = np.mean([len(sent.split()) for sent in experience_sentences]) if experience_sentences else 0
        else:
            avg_sentence_length = sum(len(sent.split()) for sent in experience_sentences) / len(experience_sentences) if experience_sentences else 0
        if avg_sentence_length >= 15:
            quality_score += 15
        elif avg_sentence_length >= 10:
            quality_score += 10
        else:
            quality_score += 5
        
        details['avg_sentence_length'] = avg_sentence_length
        
        return {
            'quality_score': min(quality_score, 100),
            'details': details,
            'experience_sentences_count': len(experience_sentences)
        }

    def _calculate_weighted_score(self, skill_analysis, ats_analysis, semantic_analysis, 
                                 experience_analysis, position: str) -> dict:
        """Calculate final weighted score based on position requirements"""
        
        # Position-specific weights
        weights = {
            'software_engineer': {'skills': 0.35, 'ats': 0.25, 'semantic': 0.25, 'experience': 0.15},
            'data_scientist': {'skills': 0.40, 'ats': 0.20, 'semantic': 0.25, 'experience': 0.15},
            'product_manager': {'skills': 0.25, 'ats': 0.25, 'semantic': 0.30, 'experience': 0.20},
            'marketing_manager': {'skills': 0.30, 'ats': 0.25, 'semantic': 0.25, 'experience': 0.20}
        }
        
        position_weights = weights.get(position, weights['software_engineer'])
        
        # Normalize scores to 0-100 scale
        skill_score = min((skill_analysis['total_skills'] * 5), 100)
        ats_score = ats_analysis['total_score']
        semantic_score = semantic_analysis['similarity_score']
        experience_score = experience_analysis['quality_score']
        
        # Calculate weighted final score
        final_score = (
            skill_score * position_weights['skills'] +
            ats_score * position_weights['ats'] +
            semantic_score * position_weights['semantic'] +
            experience_score * position_weights['experience']
        )
        
        return {
            'final_score': round(final_score, 1),
            'component_scores': {
                'skills': round(skill_score, 1),
                'ats_compatibility': round(ats_score, 1),
                'job_match': round(semantic_score, 1),
                'experience_quality': round(experience_score, 1)
            },
            'grade': self._get_final_grade(final_score),
            'percentile': self._calculate_percentile(final_score)
        }

    def _get_final_grade(self, score: float) -> str:
        """Convert final score to letter grade"""
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

    def _calculate_percentile(self, score: float) -> int:
        """Estimate percentile based on score distribution"""
        # Simulated percentile based on typical resume score distribution
        if score >= 85: return 95
        elif score >= 80: return 85
        elif score >= 75: return 75
        elif score >= 70: return 65
        elif score >= 65: return 50
        elif score >= 60: return 35
        elif score >= 55: return 25
        elif score >= 50: return 15
        else: return 5

    def _generate_precise_recommendations(self, skill_analysis, ats_analysis, 
                                        semantic_analysis, position: str) -> dict:
        """Generate precise, actionable recommendations"""
        
        recommendations = {
            'critical': [],
            'important': [],
            'enhancement': []
        }
        
        # Critical recommendations
        if ats_analysis['total_score'] < 50:
            recommendations['critical'].append({
                'category': 'ATS Compatibility',
                'issue': 'Resume may not pass ATS screening',
                'action': 'Add more action verbs and quantified achievements',
                'impact': 'High - Could prevent resume from being seen by recruiters'
            })
        
        if semantic_analysis['similarity_score'] < 40:
            recommendations['critical'].append({
                'category': 'Job Relevance',
                'issue': 'Low semantic match with job requirements',
                'action': f'Include more {position.replace("_", " ")} specific keywords and skills',
                'impact': 'High - Resume doesn\'t align with job expectations'
            })
        
        # Important recommendations
        missing_core_skills = []
        position_skills = self.skill_databases.get(position, {})
        core_skills = position_skills.get('core_skills', [])
        found_core = skill_analysis['found_skills'].get('core_skills', [])
        
        for skill in core_skills[:5]:  # Top 5 core skills
            if skill not in [s.lower() for s in found_core]:
                missing_core_skills.append(skill)
        
        if missing_core_skills:
            recommendations['important'].append({
                'category': 'Core Skills',
                'issue': f'Missing key skills: {", ".join(missing_core_skills[:3])}',
                'action': 'Add these skills to your technical skills section',
                'impact': 'Medium - Important for role qualification'
            })
        
        if ats_analysis['details']['quantified_achievements']['count'] < 3:
            recommendations['important'].append({
                'category': 'Achievement Quantification',
                'issue': 'Insufficient quantified achievements',
                'action': 'Add specific numbers, percentages, and metrics to accomplishments',
                'impact': 'Medium - Makes achievements more credible and impactful'
            })
        
        # Enhancement recommendations
        if len(semantic_analysis['matching_terms']) < 5:
            recommendations['enhancement'].append({
                'category': 'Keyword Optimization',
                'issue': 'Limited keyword overlap with job requirements',
                'action': 'Research job postings and include more relevant industry terms',
                'impact': 'Low - Improves searchability and relevance'
            })
        
        return recommendations
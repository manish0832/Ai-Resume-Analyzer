# AI Resume Analyzer

A comprehensive web application that analyzes resumes against job descriptions to provide ATS compatibility scores, skill matching analysis, and personalized improvement suggestions.

## 🎯 Features

- **ATS Compatibility Score**: Get a score out of 100 for how well your resume will perform with Applicant Tracking Systems
- **Skill Matching Analysis**: See which skills match the job requirements and which are missing
- **Improvement Suggestions**: Receive personalized recommendations to optimize your resume
- **Multiple File Formats**: Support for PDF, DOCX, DOC, and TXT files
- **Optimized Resume Export**: Download an improved version of your resume with suggestions

## 🧰 Tech Stack

- **Backend**: Flask (Python web framework)
- **NLP Processing**: scikit-learn, TF-IDF vectorization
- **File Processing**: pdfminer.six (PDF), python-docx (Word documents)
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Export**: python-docx for generating optimized resumes

## 📁 Project Structure

\`\`\`
ai-resume-analyzer/
│
├── app.py                 # Main Flask application
├── templates/
│   ├── index.html         # Upload form and landing page
│   └── result.html        # Analysis results page
├── utils/
│   ├── extract_text.py    # Text extraction from various file formats
│   ├── ats_score.py       # ATS scoring and skill matching logic
│   └── optimizer.py       # Resume optimization and suggestions
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation
\`\`\`

## 🚀 Installation

1. **Clone the repository**:
   \`\`\`bash
   git clone <repository-url>
   cd ai-resume-analyzer
   \`\`\`

2. **Create a virtual environment**:
   \`\`\`bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   \`\`\`

3. **Install dependencies**:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

4. **Run the application**:
   \`\`\`bash
   python app.py
   \`\`\`

5. **Open your browser** and navigate to \`http://localhost:5000\`

## 📊 How It Works

### 1. Text Extraction
- Extracts text from PDF files using pdfminer.six
- Processes DOCX files using python-docx
- Handles TXT files with multiple encoding support
- Cleans and normalizes extracted text

### 2. ATS Scoring Algorithm
The ATS score is calculated using multiple factors:

- **Keyword Matching (40%)**: Compares important keywords between resume and job description
- **Skills Matching (30%)**: Analyzes technical skills alignment
- **Text Similarity (20%)**: Uses TF-IDF and cosine similarity
- **Format Score (10%)**: Checks for proper resume structure and formatting

### 3. Skill Analysis
- Maintains a comprehensive database of technical skills across categories:
  - Programming languages
  - Web technologies
  - Databases
  - Cloud platforms
  - Data science tools
  - Development tools

### 4. Improvement Suggestions
Generates personalized suggestions based on:
- Missing technical skills
- Keyword optimization opportunities
- Format and structure improvements
- Content enhancement recommendations

## 🎯 Usage

1. **Upload Your Resume**: Drag and drop or select your resume file (PDF, DOCX, DOC, or TXT)
2. **Paste Job Description**: Copy the complete job posting into the text area
3. **Analyze**: Click "Analyze Resume" to process your documents
4. **Review Results**: Get your ATS score, skill matching analysis, and suggestions
5. **Download Optimized Resume**: Export an improved version with recommendations

## 📈 Score Interpretation

### ATS Compatibility Score
- **90-100**: Excellent - Very likely to pass ATS systems
- **80-89**: Good - Should pass most ATS systems
- **70-79**: Fair - May need improvements
- **Below 70**: Poor - Needs significant improvements

### Skill Match Percentage
- **80%+**: Excellent match for the role
- **60-79%**: Good match with room for improvement
- **40-59%**: Moderate match - add more relevant skills
- **Below 40%**: Low match - consider skill development

## 🔧 Customization

### Adding New Skills
Edit the \`TECHNICAL_SKILLS\` dictionary in \`utils/ats_score.py\`:

\`\`\`python
TECHNICAL_SKILLS = {
    'programming': ['python', 'java', 'javascript', ...],
    'web': ['html', 'css', 'react', ...],
    # Add new categories or skills
}
\`\`\`

### Modifying Scoring Weights
Adjust the weights in \`calculate_ats_score()\` function:

\`\`\`python
scores['keyword_match'] = keyword_score * 0.4  # 40% weight
scores['skills_match'] = skills_score * 0.3    # 30% weight
scores['text_similarity'] = similarity_score * 0.2  # 20% weight
scores['format_score'] = format_score * 0.1    # 10% weight
\`\`\`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (\`git checkout -b feature/new-feature\`)
3. Commit your changes (\`git commit -am 'Add new feature'\`)
4. Push to the branch (\`git push origin feature/new-feature\`)
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Troubleshooting

### Common Issues

1. **File Upload Errors**: Ensure files are under 16MB and in supported formats
2. **Text Extraction Issues**: Try converting your PDF to a text-searchable format
3. **Missing Dependencies**: Run \`pip install -r requirements.txt\` to install all dependencies

### Performance Tips

- Use clean, well-formatted resumes without complex layouts
- Include complete job descriptions for better analysis
- Ensure your resume has clear section headers (Experience, Education, Skills)

## 📞 Support

If you encounter any issues or have questions, please:
1. Check the troubleshooting section above
2. Review the existing issues on GitHub
3. Create a new issue with detailed information about the problem

---

**Happy job hunting! 🎯**
\`\`\`

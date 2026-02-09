import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
    Sparkles, ArrowLeft, ArrowRight, Check, Loader2,
    Briefcase, GraduationCap, MapPin, IndianRupee, Target
} from 'lucide-react';

// Quiz questions
const QUIZ_QUESTIONS = [
    {
        id: 'skills',
        question: 'What are your top skills?',
        subtitle: 'Select all that apply',
        type: 'multi',
        options: [
            { value: 'python', label: 'Python/Coding', icon: '💻' },
            { value: 'communication', label: 'Communication', icon: '🗣️' },
            { value: 'problem_solving', label: 'Problem Solving', icon: '🧩' },
            { value: 'mathematics', label: 'Mathematics', icon: '📐' },
            { value: 'creativity', label: 'Creativity', icon: '🎨' },
            { value: 'leadership', label: 'Leadership', icon: '👥' },
            { value: 'writing', label: 'Writing', icon: '✍️' },
            { value: 'analytics', label: 'Data Analytics', icon: '📊' },
        ]
    },
    {
        id: 'interests',
        question: 'What topics interest you most?',
        subtitle: 'Select all that apply',
        type: 'multi',
        options: [
            { value: 'technology', label: 'Technology', icon: '🖥️' },
            { value: 'healthcare', label: 'Healthcare', icon: '🏥' },
            { value: 'finance', label: 'Finance/Business', icon: '💰' },
            { value: 'law', label: 'Law & Justice', icon: '⚖️' },
            { value: 'arts', label: 'Arts & Design', icon: '🎭' },
            { value: 'science', label: 'Science & Research', icon: '🔬' },
            { value: 'teaching', label: 'Teaching', icon: '📚' },
            { value: 'government', label: 'Government/Civil Services', icon: '🏛️' },
        ]
    },
    {
        id: 'education_level',
        question: 'What is your current education level?',
        subtitle: 'Select one',
        type: 'single',
        options: [
            { value: '10th', label: '10th Class', icon: '🎒' },
            { value: '12th', label: '12th Class', icon: '🎓' },
            { value: 'graduate', label: 'Graduate', icon: '👨‍🎓' },
            { value: 'postgraduate', label: 'Post Graduate', icon: '🎯' },
        ]
    },
    {
        id: 'preferred_work_style',
        question: 'What is your preferred work style?',
        subtitle: 'Select one',
        type: 'single',
        options: [
            { value: 'remote', label: 'Work from Home', icon: '🏠' },
            { value: 'office', label: 'Office/On-site', icon: '🏢' },
            { value: 'hybrid', label: 'Hybrid', icon: '🔄' },
            { value: 'field', label: 'Field Work', icon: '🌍' },
        ]
    },
    {
        id: 'preferred_salary_range',
        question: 'What is your salary expectation?',
        subtitle: 'Select one',
        type: 'single',
        options: [
            { value: '3-5LPA', label: '₹3-5 LPA', icon: '💵' },
            { value: '5-10LPA', label: '₹5-10 LPA', icon: '💰' },
            { value: '10-20LPA', label: '₹10-20 LPA', icon: '💎' },
            { value: '20+LPA', label: '₹20+ LPA', icon: '🚀' },
        ]
    }
];

interface QuizAnswers {
    skills: string[];
    interests: string[];
    education_level: string;
    preferred_work_style: string;
    preferred_salary_range: string;
    [key: string]: string | string[];
}

interface CareerRecommendation {
    career_name: string;
    career_category: string;
    short_description: string;
    match_score: number;
    required_skills: string[];
    salary_range: string;
    min_education: string;
    difficulty_level: number;
    work_style: string;
}

const CareerFinder = () => {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [currentStep, setCurrentStep] = useState(0);
    const [answers, setAnswers] = useState<QuizAnswers>({
        skills: [],
        interests: [],
        education_level: '',
        preferred_work_style: '',
        preferred_salary_range: ''
    });
    const [isLoading, setIsLoading] = useState(false);
    const [recommendations, setRecommendations] = useState<CareerRecommendation[]>([]);
    const [showResults, setShowResults] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Auto-fill education level from profile
    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const res = await api.get<{ class_level?: string }>('/api/profile/profile');
                if (res.data?.class_level) {
                    // Convert class_level format (class_10 -> 10th, class_12 -> 12th)
                    let educationLevel = '';
                    if (res.data.class_level === 'class_10') {
                        educationLevel = '10th';
                    } else if (res.data.class_level === 'class_12') {
                        educationLevel = '12th';
                    }
                    if (educationLevel) {
                        setAnswers(prev => ({ ...prev, education_level: educationLevel }));
                    }
                }
            } catch (e) {
                console.error('Failed to fetch profile:', e);
            }
        };
        fetchProfile();
    }, []);

    const currentQuestion = QUIZ_QUESTIONS[currentStep];
    const progress = ((currentStep + 1) / QUIZ_QUESTIONS.length) * 100;

    const handleOptionSelect = (value: string) => {
        const questionId = currentQuestion.id;

        if (currentQuestion.type === 'multi') {
            const current = answers[questionId] as string[];
            if (current.includes(value)) {
                setAnswers({ ...answers, [questionId]: current.filter(v => v !== value) });
            } else {
                setAnswers({ ...answers, [questionId]: [...current, value] });
            }
        } else {
            setAnswers({ ...answers, [questionId]: value });
        }
    };

    const isOptionSelected = (value: string) => {
        const questionId = currentQuestion.id;
        if (currentQuestion.type === 'multi') {
            return (answers[questionId] as string[]).includes(value);
        }
        return answers[questionId] === value;
    };

    const canProceed = () => {
        const questionId = currentQuestion.id;
        if (currentQuestion.type === 'multi') {
            return (answers[questionId] as string[]).length > 0;
        }
        return answers[questionId] !== '';
    };

    const handleNext = async () => {
        if (currentStep < QUIZ_QUESTIONS.length - 1) {
            setCurrentStep(currentStep + 1);
        } else {
            // Submit quiz and get recommendations
            await submitQuiz();
        }
    };

    const handleBack = () => {
        if (currentStep > 0) {
            setCurrentStep(currentStep - 1);
        }
    };

    const submitQuiz = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const userEmail = encodeURIComponent(user?.email || '');

            // First, save quiz answers
            const quizRes = await api.post(`/api/recommendations/quiz?user_email=${userEmail}`, answers);
            if (quizRes.error) {
                console.error('Quiz save error:', quizRes.error);
                // Continue anyway to try getting recommendations
            }

            // Then get recommendations
            const res = await api.get<{ recommendations: CareerRecommendation[] }>(
                `/api/recommendations/careers?user_email=${userEmail}&top_k=5`
            );

            if (res.error) {
                setError(`API Error: ${res.error}`);
                setShowResults(true);
                return;
            }

            if (res.data?.recommendations && res.data.recommendations.length > 0) {
                setRecommendations(res.data.recommendations);
                setShowResults(true);
            } else {
                setError('No careers found. Please run the migration and seed data first.');
                setShowResults(true);
            }
        } catch (error: any) {
            console.error('Error getting recommendations:', error);
            setError(`Error: ${error.message || 'Unknown error'}`);
            setShowResults(true);
        } finally {
            setIsLoading(false);
        }
    };

    const handleViewRoadmap = async (careerName: string) => {
        // Track interaction
        try {
            const userEmail = encodeURIComponent(user?.email || '');
            await api.post(`/api/recommendations/track?user_email=${userEmail}`, {
                career_name: careerName,
                interaction_type: 'clicked_roadmap',
                source: 'recommendation'
            });
        } catch (e) {
            // Silent fail
        }
        // Navigate to backward roadmap
        navigate('/roadmap/backward', { state: { careerGoal: `I want to become a ${careerName}` } });
    };

    // Results View
    if (showResults) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 p-4">
                <div className="container mx-auto max-w-4xl">
                    <Button
                        variant="ghost"
                        onClick={() => navigate('/')}
                        className="mb-6"
                    >
                        <ArrowLeft className="h-4 w-4 mr-2" />
                        Back to Dashboard
                    </Button>

                    <div className="text-center mb-8">
                        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 mb-4">
                            <Sparkles className="h-8 w-8 text-white" />
                        </div>
                        <h1 className="text-3xl font-bold mb-2">Your Career Matches 🎯</h1>
                        <p className="text-muted-foreground">
                            Based on your skills and interests, here are your top career recommendations
                        </p>
                    </div>

                    {recommendations.length > 0 ? (
                        <div className="space-y-4">
                            {recommendations.map((career, index) => (
                                <Card
                                    key={career.career_name}
                                    className={`transition-all hover:shadow-lg ${index === 0 ? 'border-2 border-purple-500 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950/30 dark:to-pink-950/30' : ''
                                        }`}
                                >
                                    <CardContent className="p-6">
                                        <div className="flex items-start justify-between">
                                            <div className="flex-1">
                                                <div className="flex items-center gap-2 mb-2">
                                                    {index === 0 && <Badge className="bg-gradient-to-r from-purple-500 to-pink-500">Best Match</Badge>}
                                                    <Badge variant="outline" className="capitalize">{career.career_category}</Badge>
                                                </div>
                                                <h3 className="text-xl font-bold mb-1">{career.career_name}</h3>
                                                <p className="text-muted-foreground text-sm mb-3">
                                                    {career.short_description || 'A rewarding career path with great growth potential.'}
                                                </p>

                                                <div className="flex flex-wrap gap-4 text-sm mb-3">
                                                    <span className="flex items-center gap-1">
                                                        <IndianRupee className="h-4 w-4 text-green-600" />
                                                        {career.salary_range || 'Competitive'}
                                                    </span>
                                                    <span className="flex items-center gap-1">
                                                        <GraduationCap className="h-4 w-4 text-blue-600" />
                                                        {career.min_education || 'Graduate'}
                                                    </span>
                                                    <span className="flex items-center gap-1">
                                                        <Briefcase className="h-4 w-4 text-orange-600" />
                                                        {career.work_style || 'Flexible'}
                                                    </span>
                                                </div>

                                                {career.required_skills?.length > 0 && (
                                                    <div className="flex flex-wrap gap-1">
                                                        {career.required_skills.slice(0, 5).map(skill => (
                                                            <Badge key={skill} variant="secondary" className="text-xs">
                                                                {skill.replace(/_/g, ' ')}
                                                            </Badge>
                                                        ))}
                                                    </div>
                                                )}
                                            </div>

                                            <div className="text-right ml-4">
                                                <div className="text-3xl font-bold text-purple-600 dark:text-purple-400">
                                                    #{index + 1}
                                                </div>
                                                <p className="text-xs text-muted-foreground mb-3">Rank</p>
                                                <Button
                                                    onClick={() => handleViewRoadmap(career.career_name)}
                                                    className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
                                                >
                                                    <Target className="h-4 w-4 mr-2" />
                                                    View Roadmap
                                                </Button>
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    ) : (
                        <Card className="text-center p-8">
                            <CardContent>
                                {error && (
                                    <div className="bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-300 p-4 rounded-lg mb-4 text-sm">
                                        {error}
                                    </div>
                                )}
                                <p className="text-muted-foreground mb-4">
                                    We couldn't find recommendations right now. Try generating a roadmap directly!
                                </p>
                                <Button onClick={() => navigate('/roadmap')}>
                                    Go to Roadmap Generator
                                </Button>
                            </CardContent>
                        </Card>
                    )}

                    <div className="text-center mt-8">
                        <Button
                            variant="outline"
                            onClick={() => {
                                setShowResults(false);
                                setCurrentStep(0);
                                setAnswers({
                                    skills: [],
                                    interests: [],
                                    education_level: '',
                                    preferred_work_style: '',
                                    preferred_salary_range: ''
                                });
                            }}
                        >
                            Retake Quiz
                        </Button>
                    </div>
                </div>
            </div>
        );
    }

    // Quiz View
    return (
        <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 p-4">
            <div className="container mx-auto max-w-2xl">
                <Button
                    variant="ghost"
                    onClick={() => navigate('/')}
                    className="mb-6"
                >
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Back to Dashboard
                </Button>

                {/* Header */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 mb-4">
                        <Sparkles className="h-8 w-8 text-white" />
                    </div>
                    <h1 className="text-3xl font-bold mb-2">Find Your Perfect Career</h1>
                    <p className="text-muted-foreground">
                        Answer a few questions to get AI-powered career recommendations
                    </p>
                </div>

                {/* Progress */}
                <div className="mb-6">
                    <div className="flex justify-between text-sm text-muted-foreground mb-2">
                        <span>Question {currentStep + 1} of {QUIZ_QUESTIONS.length}</span>
                        <span>{Math.round(progress)}% complete</span>
                    </div>
                    <Progress value={progress} className="h-2" />
                </div>

                {/* Question Card */}
                <Card className="mb-6">
                    <CardHeader>
                        <CardTitle className="text-xl">{currentQuestion.question}</CardTitle>
                        <CardDescription>{currentQuestion.subtitle}</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-2 gap-3">
                            {currentQuestion.options.map((option) => (
                                <button
                                    key={option.value}
                                    onClick={() => handleOptionSelect(option.value)}
                                    className={`p-4 rounded-lg border-2 text-left transition-all hover:border-purple-400 ${isOptionSelected(option.value)
                                        ? 'border-purple-500 bg-purple-50 dark:bg-purple-950/30'
                                        : 'border-gray-200 dark:border-gray-700'
                                        }`}
                                >
                                    <div className="flex items-center gap-3">
                                        <span className="text-2xl">{option.icon}</span>
                                        <span className="font-medium">{option.label}</span>
                                        {isOptionSelected(option.value) && (
                                            <Check className="h-5 w-5 text-purple-500 ml-auto" />
                                        )}
                                    </div>
                                </button>
                            ))}
                        </div>
                    </CardContent>
                </Card>

                {/* Navigation */}
                <div className="flex justify-between">
                    <Button
                        variant="outline"
                        onClick={handleBack}
                        disabled={currentStep === 0}
                    >
                        <ArrowLeft className="h-4 w-4 mr-2" />
                        Back
                    </Button>

                    <Button
                        onClick={handleNext}
                        disabled={!canProceed() || isLoading}
                        className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
                    >
                        {isLoading ? (
                            <>
                                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                Finding Careers...
                            </>
                        ) : currentStep === QUIZ_QUESTIONS.length - 1 ? (
                            <>
                                Get Results
                                <Sparkles className="h-4 w-4 ml-2" />
                            </>
                        ) : (
                            <>
                                Next
                                <ArrowRight className="h-4 w-4 ml-2" />
                            </>
                        )}
                    </Button>
                </div>
            </div>
        </div>
    );
};

export default CareerFinder;

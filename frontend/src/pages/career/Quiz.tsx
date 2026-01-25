import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { ArrowLeft, ArrowRight, Loader2, CheckCircle, Sparkles } from 'lucide-react';
import { toast } from '@/hooks/use-toast';

interface QuizQuestionResponse {
  id: number;
  question_text: string;
  options: string[];
}

interface QuizAnswerSubmit {
  question_id: number;
  selected_option: number;
}

interface QuizSubmitRequest {
  answers: QuizAnswerSubmit[];
}

interface QuizResultResponse {
  stream: string | null;
}

const Quiz = () => {
  const navigate = useNavigate();
  const [questions, setQuestions] = useState<QuizQuestionResponse[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, number>[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<QuizResultResponse | null>(null);

  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        const response = await api.get<QuizQuestionResponse[]>('/api/quiz/questions');
        if (response.data) {
          setQuestions(response.data);
        }
      } catch (error: any) {
        toast({
          title: 'Error',
          description: error.response?.data?.detail || 'Failed to load quiz questions',
          variant: 'destructive',
        });
      } finally {
        setIsLoading(false);
      }
    };
    fetchQuestions();
  }, []);

  const currentQuestion = questions[currentIndex];
  const progress = questions.length > 0 ? ((currentIndex + 1) / questions.length) * 100 : 0;

  const currentAnswer = answers.find(a => a[`question_${currentQuestion?.id}`] !== undefined);

  const handleSelect = (optionIndex: number) => {
    const questionKey = `question_${currentQuestion.id}`;
    const filteredAnswers = answers.filter(a => a[questionKey] === undefined);
    filteredAnswers.push({
      [questionKey]: optionIndex,
    });
    setAnswers(filteredAnswers);
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const handleSubmit = async () => {
    if (answers.length !== questions.length) {
      toast({
        title: 'Incomplete',
        description: 'Please answer all questions before submitting',
        variant: 'destructive',
      });
      return;
    }

    setIsSubmitting(true);
    try {
      const formattedAnswers: QuizAnswerSubmit[] = answers.map(answerObj => {
        const questionKey = Object.keys(answerObj)[0];
        const questionId = parseInt(questionKey.replace('question_', ''));
        const selectedOption = answerObj[questionKey];
        
        return {
          question_id: questionId,
          selected_option: selectedOption
        };
      });

      const response = await api.post<QuizResultResponse>('/api/quiz/submit', { 
        answers: formattedAnswers 
      });
      
      if (response.data) {
        setResult(response.data);
      } else {
        toast({
          title: 'Error',
          description: response.error || 'Failed to submit quiz',
          variant: 'destructive',
        });
      }
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to submit quiz',
        variant: 'destructive',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (result) {
    return (
      <div className="min-h-screen bg-background p-4">
        <div className="container mx-auto max-w-2xl">
          <Card className="mt-8">
            <CardHeader className="text-center">
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                <Sparkles className="h-8 w-8 text-primary" />
              </div>
              <CardTitle className="text-2xl">Your Recommended Stream</CardTitle>
              <CardDescription>Based on your responses</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="text-center">
                <span className="inline-block rounded-full bg-primary px-6 py-3 text-lg font-semibold text-primary-foreground capitalize">
                  {result.stream || 'Science'}
                </span>
              </div>

              <div className="flex gap-4 pt-4">
                <Button variant="outline" className="flex-1" onClick={() => navigate('/')}>
                  Back to Dashboard
                </Button>
                <Button className="flex-1" onClick={() => navigate(`/degrees?stream=${result.stream}`)}>
                  Explore Degrees
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="container mx-auto max-w-2xl">
        <div className="mb-6 flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div className="flex-1">
            <h1 className="text-xl font-bold">Career Quiz</h1>
            <p className="text-sm text-muted-foreground">
              Question {currentIndex + 1} of {questions.length}
            </p>
          </div>
        </div>

        <Progress value={progress} className="mb-8" />

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">{currentQuestion?.question_text}</CardTitle>
          </CardHeader>
          <CardContent>
            <RadioGroup
              value={currentAnswer?.[`question_${currentQuestion?.id}`]?.toString() || ""}
              onValueChange={(value) => handleSelect(parseInt(value))}
              className="space-y-3"
            >
              {currentQuestion?.options.map((option, index) => (
                <div key={index} className="flex items-center space-x-3 rounded-lg border p-4 hover:bg-muted/50 transition-colors">
                  <RadioGroupItem value={index.toString()} id={`option-${index}`} />
                  <Label htmlFor={`option-${index}`} className="flex-1 cursor-pointer">
                    {option}
                  </Label>
                </div>
              ))}
            </RadioGroup>
          </CardContent>
        </Card>

        <div className="mt-6 flex justify-between">
          <Button
            variant="outline"
            onClick={handlePrevious}
            disabled={currentIndex === 0}
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Previous
          </Button>

          {currentIndex === questions.length - 1 ? (
            <Button onClick={handleSubmit} disabled={isSubmitting || !currentAnswer}>
              {isSubmitting ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <CheckCircle className="mr-2 h-4 w-4" />
              )}
              Submit Quiz
            </Button>
          ) : (
            <Button onClick={handleNext} disabled={!currentAnswer}>
              Next
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export default Quiz;

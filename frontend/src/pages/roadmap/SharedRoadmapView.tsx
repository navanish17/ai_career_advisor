import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { api } from '@/lib/api';
import RoadmapTimeline from '@/components/RoadmapTimeline';
import {
    BookOpen,
    Loader2,
    DollarSign,
    CheckCircle2,
    Share2
} from 'lucide-react';
import type { SavedRoadmap } from '@/types/roadmap';

const SharedRoadmapView = () => {
    const { token } = useParams<{ token: string }>();
    const [roadmap, setRoadmap] = useState<SavedRoadmap | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchSharedRoadmap = async () => {
            if (!token) return;

            try {
                // Use a direct fetch since the standard api wrapper might attach auth headers 
                // which isn't strictly wrong but for public endpoints we want to be sure
                const response = await api.get<SavedRoadmap>(`/api/roadmap/public/${token}`);

                if (response.data) {
                    setRoadmap(response.data);
                } else {
                    setError(response.error || 'Roadmap not found or access expired');
                }
            } catch (err) {
                setError('Failed to load shared roadmap');
            } finally {
                setIsLoading(false);
            }
        };

        fetchSharedRoadmap();
    }, [token]);

    if (isLoading) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                <p className="ml-2 text-muted-foreground">Loading shared roadmap...</p>
            </div>
        );
    }

    if (error || !roadmap) {
        return (
            <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4">
                <div className="bg-destructive/10 text-destructive p-6 rounded-lg text-center max-w-md">
                    <BookOpen className="h-10 w-10 mx-auto mb-4 opacity-50" />
                    <h2 className="text-xl font-bold mb-2">Unavailable</h2>
                    <p>{error || 'This roadmap link is invalid or has expired.'}</p>
                    <Button className="mt-6" asChild>
                        <Link to="/">Go to Home</Link>
                    </Button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-background">
            {/* Public Header */}
            <header className="border-b bg-muted/30 sticky top-0 z-10 backdrop-blur-md">
                <div className="container mx-auto flex h-16 items-center justify-between px-4">
                    <div className="flex items-center gap-2">
                        <div className="bg-primary/10 p-2 rounded-lg">
                            <BookOpen className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                            <span className="font-bold text-lg block leading-none">AI Career Pilot</span>
                            <span className="text-[10px] text-muted-foreground uppercase tracking-widest">Shared View</span>
                        </div>
                    </div>

                    <div className="flex gap-2">
                        <Button asChild size="sm" variant="outline">
                            <Link to="/auth/login">Login to Create Yours</Link>
                        </Button>
                        <Button asChild size="sm">
                            <Link to="/auth/signup">Get Started</Link>
                        </Button>
                    </div>
                </div>
            </header>

            <main className="container mx-auto p-4 max-w-4xl py-8">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
                    <div>
                        <Badge variant="outline" className="mb-2 capitalize">
                            {roadmap.type} Roadmap
                        </Badge>
                        <h1 className="text-3xl font-bold tracking-tight text-foreground">{roadmap.name}</h1>
                        <p className="text-muted-foreground mt-1">
                            Shared career plan for becoming a <span className="font-medium text-foreground">{roadmap.roadmap_data?.career_name}</span>
                        </p>
                    </div>

                    <div className="flex items-center gap-2 text-xs text-muted-foreground bg-muted p-2 rounded-md">
                        <Share2 className="h-3 w-3" />
                        Read-only View
                    </div>
                </div>

                {/* Display different content based on roadmap type */}
                {roadmap.type === 'backward' && roadmap.roadmap_data?.normalized_career ? (
                    <RoadmapTimeline
                        roadmapData={roadmap.roadmap_data}
                        source={roadmap.roadmap_data.source || 'Database'}
                        showSaveButton={false} // Always false for shared view
                    />
                ) : (
                    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                        {/* STEP 1: CURRENT EDUCATION LEVEL */}
                        <Card className="border-l-4 border-l-blue-500 shadow-sm">
                            <CardHeader>
                                <CardTitle className="text-xl flex items-center gap-3">
                                    <span className="inline-flex items-center justify-center w-8 h-8 bg-blue-500 text-white rounded-full font-bold text-sm">1</span>
                                    Current Stage
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="bg-blue-50/50 dark:bg-blue-950/20 p-4 rounded-lg border border-blue-100 dark:border-blue-900">
                                        <p className="text-xs text-muted-foreground uppercase font-semibold mb-1">Education Level</p>
                                        <p className="text-xl font-bold text-blue-700 dark:text-blue-300">
                                            {roadmap.roadmap_data?.class_level?.replace('class_', 'Class ') || 'N/A'}
                                        </p>
                                    </div>
                                    <div className="bg-blue-50/50 dark:bg-blue-950/20 p-4 rounded-lg border border-blue-100 dark:border-blue-900">
                                        <p className="text-xs text-muted-foreground uppercase font-semibold mb-1">Status</p>
                                        <p className="text-base font-bold text-blue-700 dark:text-blue-300 pt-1">Current Student</p>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        {/* STEP 2: STREAM SELECTION */}
                        <Card className="border-l-4 border-l-purple-500 shadow-sm">
                            <CardHeader>
                                <CardTitle className="text-xl flex items-center gap-3">
                                    <span className="inline-flex items-center justify-center w-8 h-8 bg-purple-500 text-white rounded-full font-bold text-sm">2</span>
                                    Stream Choice
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="bg-purple-50/50 dark:bg-purple-950/20 p-4 rounded-lg border border-purple-100 dark:border-purple-900">
                                    <p className="text-xs text-muted-foreground uppercase font-semibold mb-2">Selected Stream</p>
                                    <p className="text-2xl font-bold text-purple-700 dark:text-purple-300 capitalize">
                                        {roadmap.roadmap_data?.stream || 'N/A'}
                                    </p>
                                    <p className="text-sm text-muted-foreground mt-2">
                                        {roadmap.roadmap_data?.stream === 'science' && 'Engineering, Medical, Research & Tech'}
                                        {roadmap.roadmap_data?.stream === 'commerce' && 'Business, Finance, Accounting & Economics'}
                                        {roadmap.roadmap_data?.stream === 'arts' && 'Humanities, Design, Media & Social Sciences'}
                                    </p>
                                </div>
                            </CardContent>
                        </Card>

                        {/* STEP 3: DEGREE PROGRAM */}
                        <Card className="border-l-4 border-l-green-500 shadow-sm">
                            <CardHeader>
                                <CardTitle className="text-xl flex items-center gap-3">
                                    <span className="inline-flex items-center justify-center w-8 h-8 bg-green-500 text-white rounded-full font-bold text-sm">3</span>
                                    Degree Path
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="bg-green-50/50 dark:bg-green-950/20 p-4 rounded-lg border border-green-100 dark:border-green-900 space-y-3">
                                    <div>
                                        <p className="text-xs text-muted-foreground uppercase font-semibold mb-1">Recommended Degree</p>
                                        <p className="text-2xl font-bold text-green-700 dark:text-green-300">
                                            {roadmap.roadmap_data?.degree_name || 'N/A'}
                                        </p>
                                    </div>

                                    {roadmap.roadmap_data?.degree_duration && (
                                        <div className="border-t border-green-200 dark:border-green-800 pt-3">
                                            <div className="flex justify-between items-center">
                                                <span className="text-sm text-green-800 dark:text-green-200">Duration</span>
                                                <span className="font-bold text-green-700 dark:text-green-300">{roadmap.roadmap_data.degree_duration} Years</span>
                                            </div>
                                        </div>
                                    )}

                                    {roadmap.roadmap_data?.degree_description && (
                                        <div className="pt-2">
                                            <p className="text-sm text-green-900 dark:text-green-100 italic">
                                                "{roadmap.roadmap_data.degree_description}"
                                            </p>
                                        </div>
                                    )}
                                </div>
                            </CardContent>
                        </Card>

                        {/* STEP 4: CAREER GOAL */}
                        <Card className="border-l-4 border-l-orange-500 shadow-sm">
                            <CardHeader>
                                <CardTitle className="text-xl flex items-center gap-3">
                                    <span className="inline-flex items-center justify-center w-8 h-8 bg-orange-500 text-white rounded-full font-bold text-sm">4</span>
                                    Career Destination
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="bg-orange-50/50 dark:bg-orange-950/20 p-4 rounded-lg border border-orange-100 dark:border-orange-900 space-y-3">
                                    <div>
                                        <p className="text-xs text-muted-foreground uppercase font-semibold mb-1">Target Role</p>
                                        <p className="text-3xl font-bold text-orange-700 dark:text-orange-300">
                                            {roadmap.roadmap_data?.career_name || 'N/A'}
                                        </p>
                                    </div>

                                    {roadmap.roadmap_data?.career_salary_range && (
                                        <div className="border-t border-orange-200 dark:border-orange-800 pt-3">
                                            <p className="text-xs text-muted-foreground uppercase font-semibold mb-1">Potential Salary</p>
                                            <p className="text-xl font-bold text-orange-700 dark:text-orange-300 flex items-center gap-1">
                                                <DollarSign className="h-5 w-5" />
                                                {roadmap.roadmap_data.career_salary_range}
                                            </p>
                                        </div>
                                    )}
                                </div>
                            </CardContent>
                        </Card>

                        {/* SUMMARY JOURNEY */}
                        <Card className="bg-gradient-to-r from-primary/10 to-primary/5 border-primary/20">
                            <CardHeader>
                                <CardTitle className="text-lg">Summary</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3 text-sm">
                                    <p>
                                        <strong>Path:</strong> {roadmap.roadmap_data?.class_level?.replace('class_', 'Class ')} → {roadmap.roadmap_data?.degree_name} → {roadmap.roadmap_data?.custom_career ?? roadmap.roadmap_data?.career_name}
                                    </p>
                                </div>

                                <div className="mt-6 flex justify-center">
                                    <Button asChild className="w-full sm:w-auto">
                                        <Link to="/auth/signup">Create Your Own Roadmap Free</Link>
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                )}
            </main>
        </div>
    );
};

export default SharedRoadmapView;

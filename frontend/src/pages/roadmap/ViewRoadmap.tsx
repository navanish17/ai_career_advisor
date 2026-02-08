import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import RoadmapTimeline from '@/components/RoadmapTimeline';
import {
  BookOpen,
  ArrowLeft,
  Loader2,
  Trash2,
  GraduationCap,
  BookOpenCheck,
  Target,
  Zap,
  Briefcase,
  DollarSign,
  Star,
  CheckCircle2,
  Share2,
  Link as LinkIcon,
  Copy,
  Download,
  Mail,
  Smartphone
} from 'lucide-react';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { SavedRoadmap } from '@/types/roadmap';

const ViewRoadmap = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const { toast } = useToast();

  const [roadmap, setRoadmap] = useState<SavedRoadmap | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showShareDialog, setShowShareDialog] = useState(false);
  const [shareLink, setShareLink] = useState('');
  const [isSharing, setIsSharing] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    const fetchRoadmap = async () => {
      if (!id) return;
      const response = await api.get<SavedRoadmap>(`/api/roadmap/saved/${id}`);
      if (response.data) {
        setRoadmap(response.data);
      } else {
        toast({
          title: 'Roadmap not found',
          description: response.error || 'Could not load roadmap',
          variant: 'destructive'
        });
        navigate('/roadmap/my-roadmaps');
      }
      setIsLoading(false);
    };
    fetchRoadmap();
  }, [id, navigate, toast]);

  const handleDelete = async () => {
    if (!id) return;

    setIsDeleting(true);
    const response = await api.delete(`/api/roadmap/roadmap/${id}`);

    if (response.error) {
      toast({
        title: 'Delete failed',
        description: response.error,
        variant: 'destructive'
      });
      setIsDeleting(false);
    } else {
      toast({
        title: 'Roadmap deleted',
        description: 'The roadmap has been removed'
      });
      navigate('/roadmap/my-roadmaps');
    }
  };

  const handleShare = async () => {
    if (!id) return;
    setIsSharing(true);

    // If we already have a token from previous fetch (we need to update API to return it first)
    // For now, let's just hit the endpoint to ensure we have a fresh token/link
    const response = await api.post<{ share_token: string }>(`/api/roadmap/${id}/share`, {});

    if (response.data) {
      const link = `${window.location.origin}/roadmap/shared/${response.data.share_token}`;
      setShareLink(link);
      setShowShareDialog(true);
    } else {
      toast({
        title: 'Share failed',
        description: response.error || 'Could not generate share link',
        variant: 'destructive'
      });
    }
    setIsSharing(false);
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(shareLink);
    toast({
      title: 'Link copied',
      description: 'Share link copied to clipboard'
    });
  };

  const handleDownloadPDF = async () => {
    const element = document.getElementById('roadmap-content');
    if (!element) return;

    setIsDownloading(true);
    try {
      const canvas = await html2canvas(element, {
        scale: 2, // Improve quality
        useCORS: true,
        logging: false
      });

      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4'
      });

      const imgWidth = 210; // A4 width in mm
      const pageHeight = 297; // A4 height in mm
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      let heightLeft = imgHeight;
      let position = 0;

      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;

      while (heightLeft >= 0) {
        position = heightLeft - imgHeight;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;
      }

      pdf.save(`${roadmap?.name || 'roadmap'}.pdf`);

      toast({
        title: 'Download complete',
        description: 'Roadmap saved as PDF'
      });
    } catch (error) {
      console.error('PDF generation failed:', error);
      toast({
        title: 'Download failed',
        description: 'Could not generate PDF',
        variant: 'destructive'
      });
    } finally {
      setIsDownloading(false);
    }
  };

  const shareViaWhatsApp = () => {
    const text = `Check out my career roadmap: ${roadmap?.name}`;
    const url = `https://wa.me/?text=${encodeURIComponent(text + ' ' + shareLink)}`;
    window.open(url, '_blank');
  };

  const shareViaEmail = () => {
    const subject = `Career Roadmap: ${roadmap?.name}`;
    const body = `Hi,\n\nCheck out my career roadmap "${roadmap?.name}" here:\n${shareLink}\n\nCreated with AI Career Pilot.`;
    window.open(`mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!roadmap) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <BookOpen className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">AI Career Pilot</span>
          </div>
          <Button variant="ghost" onClick={() => navigate('/roadmap/my-roadmaps')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to My Roadmaps
          </Button>
        </div>
      </header>

      <main className="container mx-auto p-4 max-w-4xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">{roadmap.name}</h1>
            <p className="text-sm text-muted-foreground capitalize">
              {roadmap.type} Plan • Created {new Date(roadmap.created_at).toLocaleDateString()}
            </p>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={handleShare}
              disabled={isSharing}
            >
              {isSharing ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Share2 className="h-4 w-4 mr-2" />}
              Share
            </Button>
            <Button
              variant="outline"
              className="text-destructive hover:text-destructive"
              onClick={() => setShowDeleteDialog(true)}
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Delete
            </Button>
          </div>
        </div>

        <div id="roadmap-content" className="max-w-4xl mx-auto">
          {/* Display different content based on roadmap type */}
          {roadmap.type === 'backward' && roadmap.roadmap_data?.normalized_career ? (
            <RoadmapTimeline
              roadmapData={roadmap.roadmap_data}
              source={roadmap.roadmap_data.source || 'Database'}
              showSaveButton={false}
            />
          ) : (
            <div className="space-y-6">
              {/* STEP 1: CURRENT EDUCATION LEVEL */}
              <Card className="border-l-4 border-l-blue-500">
                <CardHeader>
                  <CardTitle className="text-2xl flex items-center gap-3">
                    <span className="inline-flex items-center justify-center w-8 h-8 bg-blue-500 text-white rounded-full font-bold">1</span>
                    Current Education Level
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">Class Level</p>
                      <p className="text-2xl font-bold text-blue-700 dark:text-blue-300">
                        {roadmap.roadmap_data?.class_level?.replace('class_', 'Class ') || 'N/A'}
                      </p>
                    </div>
                    <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">Status</p>
                      <p className="text-lg font-bold text-blue-700 dark:text-blue-300">Current Student</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* STEP 2: STREAM SELECTION */}
              <Card className="border-l-4 border-l-purple-500">
                <CardHeader>
                  <CardTitle className="text-2xl flex items-center gap-3">
                    <span className="inline-flex items-center justify-center w-8 h-8 bg-purple-500 text-white rounded-full font-bold">2</span>
                    Stream Selection
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="bg-purple-50 dark:bg-purple-950 p-4 rounded-lg">
                    <p className="text-sm text-muted-foreground mb-2">Your Stream</p>
                    <p className="text-3xl font-bold text-purple-700 dark:text-purple-300 capitalize">
                      {roadmap.roadmap_data?.stream || 'N/A'}
                    </p>
                    <p className="text-sm text-muted-foreground mt-3">
                      {roadmap.roadmap_data?.stream === 'science' && 'Science stream - Best for engineering, medicine, research careers'}
                      {roadmap.roadmap_data?.stream === 'commerce' && 'Commerce stream - Best for business, finance, accounting careers'}
                      {roadmap.roadmap_data?.stream === 'arts' && 'Arts stream - Best for humanities, social science careers'}
                    </p>
                  </div>
                </CardContent>
              </Card>

              {/* STEP 3: DEGREE PROGRAM */}
              <Card className="border-l-4 border-l-green-500">
                <CardHeader>
                  <CardTitle className="text-2xl flex items-center gap-3">
                    <span className="inline-flex items-center justify-center w-8 h-8 bg-green-500 text-white rounded-full font-bold">3</span>
                    Degree Program
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="bg-green-50 dark:bg-green-950 p-4 rounded-lg space-y-3">
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Degree Name</p>
                      <p className="text-2xl font-bold text-green-700 dark:text-green-300">
                        {roadmap.roadmap_data?.degree_name || 'N/A'}
                      </p>
                    </div>

                    {roadmap.roadmap_data?.degree_duration && (
                      <div className="border-t border-green-200 dark:border-green-800 pt-3">
                        <p className="text-sm text-muted-foreground mb-1">Duration</p>
                        <p className="text-lg font-semibold text-green-700 dark:text-green-300">
                          {roadmap.roadmap_data.degree_duration} Years
                        </p>
                      </div>
                    )}

                    {roadmap.roadmap_data?.degree_description && (
                      <div className="border-t border-green-200 dark:border-green-800 pt-3">
                        <p className="text-sm text-muted-foreground mb-1">Description</p>
                        <p className="text-sm text-green-900 dark:text-green-100">
                          {roadmap.roadmap_data.degree_description}
                        </p>
                      </div>
                    )}

                    {roadmap.roadmap_data?.degree_eligibility && (
                      <div className="border-t border-green-200 dark:border-green-800 pt-3">
                        <p className="text-sm text-muted-foreground mb-1">Eligibility</p>
                        <p className="text-sm text-green-900 dark:text-green-100">
                          {roadmap.roadmap_data.degree_eligibility}
                        </p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* STEP 4: SPECIALIZATION/BRANCH */}
              <Card className="border-l-4 border-l-blue-600">
                <CardHeader>
                  <CardTitle className="text-2xl flex items-center gap-3">
                    <span className="inline-flex items-center justify-center w-8 h-8 bg-blue-600 text-white rounded-full font-bold">4</span>
                    Specialization / Branch
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg">
                    <p className="text-sm text-muted-foreground mb-2">Branch Name</p>
                    <p className="text-2xl font-bold text-blue-700 dark:text-blue-300">
                      {roadmap.roadmap_data?.branch_name || 'N/A'}
                    </p>
                    <p className="text-sm text-muted-foreground mt-3">
                      Specialization in {roadmap.roadmap_data?.degree_name || 'your degree'}
                    </p>
                  </div>
                </CardContent>
              </Card>

              {/* STEP 5: CAREER PATH */}
              <Card className="border-l-4 border-l-orange-500">
                <CardHeader>
                  <CardTitle className="text-2xl flex items-center gap-3">
                    <span className="inline-flex items-center justify-center w-8 h-8 bg-orange-500 text-white rounded-full font-bold">5</span>
                    Target Career
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="bg-orange-50 dark:bg-orange-950 p-4 rounded-lg space-y-3">
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Career Title</p>
                      <p className="text-3xl font-bold text-orange-700 dark:text-orange-300">
                        {roadmap.roadmap_data?.career_name || 'N/A'}
                      </p>
                    </div>

                    {roadmap.roadmap_data?.career_salary_range && (
                      <div className="border-t border-orange-200 dark:border-orange-800 pt-3">
                        <p className="text-sm text-muted-foreground mb-1">Salary Range</p>
                        <p className="text-2xl font-bold text-orange-700 dark:text-orange-300 flex items-center gap-1">
                          <DollarSign className="h-5 w-5" />
                          {roadmap.roadmap_data.career_salary_range}
                        </p>
                      </div>
                    )}

                    {roadmap.roadmap_data?.career_description && (
                      <div className="border-t border-orange-200 dark:border-orange-800 pt-3">
                        <p className="text-sm text-muted-foreground mb-2">Role Description</p>
                        <p className="text-sm text-orange-900 dark:text-orange-100">
                          {roadmap.roadmap_data.career_description}
                        </p>
                      </div>
                    )}

                    {roadmap.roadmap_data?.career_market_trend && (
                      <div className="border-t border-orange-200 dark:border-orange-800 pt-3">
                        <p className="text-sm text-muted-foreground mb-1">Market Status</p>
                        <Badge className="bg-green-500 text-white">
                          {roadmap.roadmap_data.career_market_trend}
                        </Badge>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* STEP 6: TOP 1% PROFESSIONAL REQUIREMENTS */}
              {roadmap.roadmap_data?.career_insights && (
                <Card className="border-l-4 border-l-amber-500 bg-gradient-to-r from-amber-50 to-yellow-50 dark:from-amber-950 dark:to-yellow-950">
                  <CardHeader>
                    <CardTitle className="text-2xl flex items-center gap-3 text-amber-900 dark:text-amber-100">
                      <span className="inline-flex items-center justify-center w-8 h-8 bg-amber-500 text-white rounded-full font-bold">6</span>
                      Top 1% Professional Requirements
                    </CardTitle>
                    <CardDescription className="text-amber-800 dark:text-amber-200">
                      Master these to become a top performer in your field
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* Top Salary */}
                    {roadmap.roadmap_data.career_insights.top_salary && (
                      <div className="bg-white dark:bg-slate-800 p-4 rounded-lg border-2 border-amber-500">
                        <p className="text-sm text-muted-foreground mb-1">Top Earner Salary Range</p>
                        <p className="text-3xl font-bold text-amber-600 dark:text-amber-400">
                          {roadmap.roadmap_data.career_insights.top_salary}
                        </p>
                        <p className="text-xs text-muted-foreground mt-2">Achievable with expertise and experience</p>
                      </div>
                    )}

                    {/* Skills Required */}
                    {roadmap.roadmap_data.career_insights.skills && roadmap.roadmap_data.career_insights.skills.length > 0 && (
                      <div>
                        <h4 className="font-bold text-amber-900 dark:text-amber-100 mb-3 text-lg">
                          Essential Technical & Soft Skills
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {roadmap.roadmap_data.career_insights.skills.map((skill, idx) => (
                            <Badge key={idx} className="bg-amber-600 hover:bg-amber-700 text-white text-sm py-1 px-3">
                              {skill}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Certifications & Programs */}
                    {roadmap.roadmap_data.career_insights.programs && roadmap.roadmap_data.career_insights.programs.length > 0 && (
                      <div className="bg-white dark:bg-slate-800 p-4 rounded-lg">
                        <h4 className="font-bold text-amber-900 dark:text-amber-100 mb-3">
                          Recommended Certifications & Programs
                        </h4>
                        <ul className="space-y-2">
                          {roadmap.roadmap_data.career_insights.programs.map((program, idx) => (
                            <li key={idx} className="flex items-start gap-3">
                              <CheckCircle2 className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
                              <span className="text-sm text-gray-700 dark:text-gray-300">{program}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Internships */}
                    {roadmap.roadmap_data.career_insights.internships && roadmap.roadmap_data.career_insights.internships.length > 0 && (
                      <div className="bg-white dark:bg-slate-800 p-4 rounded-lg">
                        <h4 className="font-bold text-amber-900 dark:text-amber-100 mb-3">
                          Recommended Internship Opportunities
                        </h4>
                        <ul className="space-y-2">
                          {roadmap.roadmap_data.career_insights.internships.map((internship, idx) => (
                            <li key={idx} className="flex items-start gap-3">
                              <CheckCircle2 className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
                              <span className="text-sm text-gray-700 dark:text-gray-300">{internship}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Projects */}
                    {roadmap.roadmap_data.career_insights.projects && (
                      <div className="space-y-4">
                        {roadmap.roadmap_data.career_insights.projects.production && roadmap.roadmap_data.career_insights.projects.production.length > 0 && (
                          <div className="bg-white dark:bg-slate-800 p-4 rounded-lg">
                            <h4 className="font-bold text-amber-900 dark:text-amber-100 mb-3">
                              Production Projects to Build
                            </h4>
                            <ul className="space-y-2">
                              {roadmap.roadmap_data.career_insights.projects.production.map((project, idx) => (
                                <li key={idx} className="flex items-start gap-3">
                                  <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                                  <span className="text-sm text-gray-700 dark:text-gray-300">{project}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {roadmap.roadmap_data.career_insights.projects.research && roadmap.roadmap_data.career_insights.projects.research.length > 0 && (
                          <div className="bg-white dark:bg-slate-800 p-4 rounded-lg">
                            <h4 className="font-bold text-amber-900 dark:text-amber-100 mb-3">
                              Research Projects & Papers
                            </h4>
                            <ul className="space-y-2">
                              {roadmap.roadmap_data.career_insights.projects.research.map((project, idx) => (
                                <li key={idx} className="flex items-start gap-3">
                                  <CheckCircle2 className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                                  <span className="text-sm text-gray-700 dark:text-gray-300">{project}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* SUMMARY JOURNEY */}
              <Card className="bg-gradient-to-r from-primary/10 to-primary/5">
                <CardHeader>
                  <CardTitle>Your Complete Career Journey</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 text-sm">
                    <p>
                      <strong>📚 Educational Path:</strong> Start from {roadmap.roadmap_data?.class_level?.replace('class_', 'Class ')} ({roadmap.roadmap_data?.stream} stream) →
                      Complete {roadmap.roadmap_data?.degree_name} ({roadmap.roadmap_data?.degree_duration || '4'} years) →
                      Specialize in {roadmap.roadmap_data?.branch_name}
                    </p>
                    <p>
                      <strong>💼 Career Goal:</strong> Become a {roadmap.roadmap_data?.career_name} with expertise and professional recognition
                    </p>
                    <p>
                      <strong>🎯 Expected Outcome:</strong> Top 1% professionals in {roadmap.roadmap_data?.career_name} field earn {roadmap.roadmap_data?.career_insights?.top_salary || 'competitive salary'}
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>

        {/* Delete Confirmation Dialog */}
        <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Delete Roadmap?</AlertDialogTitle>
              <AlertDialogDescription>
                This action cannot be undone. This will permanently delete "{roadmap.name}".
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction
                onClick={handleDelete}
                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                disabled={isDeleting}
              >
                {isDeleting ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
                Delete
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>

        {/* Share Dialog */}
        <Dialog open={showShareDialog} onOpenChange={setShowShareDialog}>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Share Roadmap</DialogTitle>
              <DialogDescription>
                Anyone with this link can view this roadmap.
              </DialogDescription>
            </DialogHeader>
            <div className="flex items-center space-x-2">
              <div className="grid flex-1 gap-2">
                <Label htmlFor="link" className="sr-only">
                  Link
                </Label>
                <Input
                  id="link"
                  defaultValue={shareLink}
                  readOnly
                />
              </div>
              <Button type="submit" size="sm" className="px-3" onClick={copyToClipboard}>
                <span className="sr-only">Copy</span>
                <Copy className="h-4 w-4" />
              </Button>
            </div>

            <div className="grid grid-cols-3 gap-2 py-4">
              <Button variant="outline" className="flex flex-col h-20 gap-1 items-center justify-center" onClick={shareViaWhatsApp}>
                <Smartphone className="h-6 w-6 text-green-500" />
                <span className="text-xs">WhatsApp</span>
              </Button>
              <Button variant="outline" className="flex flex-col h-20 gap-1 items-center justify-center" onClick={shareViaEmail}>
                <Mail className="h-6 w-6 text-blue-500" />
                <span className="text-xs">Email</span>
              </Button>
              <Button variant="outline" className="flex flex-col h-20 gap-1 items-center justify-center" onClick={handleDownloadPDF} disabled={isDownloading}>
                {isDownloading ? <Loader2 className="h-6 w-6 animate-spin" /> : <Download className="h-6 w-6 text-orange-500" />}
                <span className="text-xs">Download PDF</span>
              </Button>
            </div>

            <DialogFooter className="sm:justify-start">
              <Button
                type="button"
                variant="secondary"
                onClick={() => setShowShareDialog(false)}
              >
                Close
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </main>
    </div>
  );
};

export default ViewRoadmap;

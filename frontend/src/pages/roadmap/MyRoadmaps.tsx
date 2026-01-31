import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import {
  BookOpen,
  ArrowLeft,
  Plus,
  Target,
  Loader2,
  Trash2,
  Eye,
  FolderOpen,
  Calendar
} from 'lucide-react';
import type { SavedRoadmap } from '@/types/roadmap';

const MyRoadmaps = () => {
  const navigate = useNavigate();
  const { toast } = useToast();

  const [roadmaps, setRoadmaps] = useState<SavedRoadmap[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    fetchRoadmaps();
  }, []);

  const fetchRoadmaps = async () => {
    const response = await api.get<SavedRoadmap[]>('/api/roadmap/user');
    if (response.data) {
      setRoadmaps(response.data);
    }
    setIsLoading(false);
  };

  const handleDelete = async () => {
    if (!deleteId) return;

    setIsDeleting(true);
    const response = await api.delete(`/api/roadmap/roadmap/${deleteId}`);

    if (response.error) {
      toast({
        title: 'Delete failed',
        description: response.error,
        variant: 'destructive'
      });
    } else {
      toast({
        title: 'Roadmap deleted',
        description: 'The roadmap has been removed'
      });
      setRoadmaps(roadmaps.filter(r => r.id !== deleteId));
    }

    setIsDeleting(false);
    setDeleteId(null);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <BookOpen className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">AI Career Pilot</span>
          </div>
          <Button variant="ghost" onClick={() => navigate('/roadmap')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Roadmap Hub
          </Button>
        </div>
      </header>

      <main className="container mx-auto p-4 max-w-4xl">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <FolderOpen className="h-8 w-8 text-primary" />
              My Saved Roadmaps
            </h1>
            <p className="text-muted-foreground mt-1">
              View and manage your career roadmaps
            </p>
          </div>
          <Button onClick={() => navigate('/roadmap')}>
            <Plus className="h-4 w-4 mr-2" />
            New Roadmap
          </Button>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : roadmaps.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <FolderOpen className="h-16 w-16 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No saved roadmaps yet</h3>
              <p className="text-muted-foreground text-center mb-4">
                Create your first career roadmap and save it for future reference
              </p>
              <Button onClick={() => navigate('/roadmap')}>
                <Plus className="h-4 w-4 mr-2" />
                Create Roadmap
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {roadmaps.map((roadmap) => (
              <Card key={roadmap.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <div className="p-2 rounded-lg bg-primary/10">
                        <Target className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <CardTitle className="text-lg">{roadmap.name}</CardTitle>
                        <CardDescription className="flex items-center gap-2 mt-1">
                          <Badge variant="outline" className="capitalize">
                            {roadmap.type} Plan
                          </Badge>
                          <span className="flex items-center gap-1 text-xs">
                            <Calendar className="h-3 w-3" />
                            {new Date(roadmap.created_at).toLocaleDateString()}
                          </span>
                        </CardDescription>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => navigate(`/roadmap/view/${roadmap.id}`)}
                      >
                        <Eye className="h-4 w-4 mr-1" />
                        View
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-destructive hover:text-destructive"
                        onClick={() => setDeleteId(roadmap.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                {roadmap.career_goal && (
                  <CardContent className="pt-0">
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      Goal: {roadmap.career_goal}
                    </p>
                  </CardContent>
                )}
              </Card>
            ))}
          </div>
        )}

        {/* Delete Confirmation Dialog */}
        <AlertDialog open={!!deleteId} onOpenChange={() => setDeleteId(null)}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Delete Roadmap?</AlertDialogTitle>
              <AlertDialogDescription>
                This action cannot be undone. This will permanently delete the roadmap.
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
      </main>
    </div>
  );
};

export default MyRoadmaps;

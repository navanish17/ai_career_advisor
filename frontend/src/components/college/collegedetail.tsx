import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ExternalLink, MapPin, Building2, Trophy, GraduationCap, Briefcase, IndianRupee } from 'lucide-react';
import { AlertSetupForm } from './alertsetupform';
import type { CollegeDetail, AlertType } from '@/types/college';

interface CollegeDetailDialogProps {
  college: CollegeDetail | null;
  degree: string;
  branch: string;
  userEmail?: string;
  isOpen: boolean;
  onClose: () => void;
  onSetAlert: (email: string, alertTypes: AlertType[]) => Promise<void>;
  isSettingAlert?: boolean;
}

export const CollegeDetailDialog = ({
  college,
  degree,
  branch,
  userEmail = '',
  isOpen,
  onClose,
  onSetAlert,
  isSettingAlert = false,
}: CollegeDetailDialogProps) => {
  if (!college) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-xl">{college.name}</DialogTitle>
          <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
            {college.location && (
              <span className="flex items-center gap-1">
                <MapPin className="h-3.5 w-3.5" />
                {college.location}
              </span>
            )}
            {college.established && (
              <span className="flex items-center gap-1">
                <Building2 className="h-3.5 w-3.5" />
                Est. {college.established}
              </span>
            )}
            {college.nirf_rank && (
              <Badge variant="secondary">
                <Trophy className="h-3 w-3 mr-1" />
                #{college.nirf_rank} NIRF
              </Badge>
            )}
          </div>
        </DialogHeader>

        <Tabs defaultValue="details" className="mt-4">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="details">College Details</TabsTrigger>
            <TabsTrigger value="alerts">Set Alerts</TabsTrigger>
          </TabsList>

          <TabsContent value="details" className="space-y-4 mt-4">
            {/* Program Info */}
            <div>
              <h4 className="font-semibold flex items-center gap-2 mb-2">
                <GraduationCap className="h-4 w-4 text-primary" />
                Program Information
              </h4>
              <div className="grid grid-cols-2 gap-3 text-sm bg-muted/50 p-3 rounded-lg">
                <div>
                  <p className="text-muted-foreground">Degree</p>
                  <p className="font-medium">{degree}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Branch</p>
                  <p className="font-medium">{branch}</p>
                </div>
                {college.duration && (
                  <div>
                    <p className="text-muted-foreground">Duration</p>
                    <p className="font-medium">{college.duration}</p>
                  </div>
                )}
                {college.seats && (
                  <div>
                    <p className="text-muted-foreground">Total Seats</p>
                    <p className="font-medium">{college.seats}</p>
                  </div>
                )}
              </div>
            </div>

            <Separator />

            {/* Admission Details */}
            {(college.entrance_exam || college.cutoff) && (
              <>
                <div>
                  <h4 className="font-semibold mb-2">Admission Details</h4>
                  <div className="grid grid-cols-2 gap-3 text-sm bg-muted/50 p-3 rounded-lg">
                    {college.entrance_exam && (
                      <div>
                        <p className="text-muted-foreground">Entrance Exam</p>
                        <p className="font-medium">{college.entrance_exam}</p>
                      </div>
                    )}
                    {college.cutoff && (
                      <div>
                        <p className="text-muted-foreground">Cutoff</p>
                        <p className="font-medium">{college.cutoff}</p>
                      </div>
                    )}
                  </div>
                </div>
                <Separator />
              </>
            )}

            {/* Fees */}
            {college.fees && (
              <>
                <div>
                  <h4 className="font-semibold flex items-center gap-2 mb-2">
                    <IndianRupee className="h-4 w-4 text-primary" />
                    Fees
                  </h4>
                  <p className="text-lg font-medium">{college.fees}</p>
                </div>
                <Separator />
              </>
            )}

            {/* Placements */}
            {(college.avg_package || college.highest_package) && (
              <>
                <div>
                  <h4 className="font-semibold flex items-center gap-2 mb-2">
                    <Briefcase className="h-4 w-4 text-primary" />
                    Placements
                  </h4>
                  <div className="grid grid-cols-2 gap-3 text-sm bg-muted/50 p-3 rounded-lg">
                    {college.avg_package && (
                      <div>
                        <p className="text-muted-foreground">Average Package</p>
                        <p className="font-medium text-lg">{college.avg_package}</p>
                      </div>
                    )}
                    {college.highest_package && (
                      <div>
                        <p className="text-muted-foreground">Highest Package</p>
                        <p className="font-medium text-lg">{college.highest_package}</p>
                      </div>
                    )}
                  </div>
                </div>
                <Separator />
              </>
            )}

            {/* Top Recruiters */}
            {college.top_recruiters && college.top_recruiters.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2">Top Recruiters</h4>
                <div className="flex flex-wrap gap-2">
                  {college.top_recruiters.map((recruiter, idx) => (
                    <Badge key={idx} variant="outline">
                      {recruiter}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Official Website */}
            {college.official_website && (
              <a
                href={college.official_website}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-sm text-primary hover:underline"
              >
                Visit Official Website
                <ExternalLink className="h-3.5 w-3.5" />
              </a>
            )}
          </TabsContent>

          <TabsContent value="alerts" className="mt-4">
            <div className="space-y-4">
              <div className="bg-muted/50 p-3 rounded-lg text-sm">
                <p className="font-medium mb-1">Set admission alerts for:</p>
                <p className="text-muted-foreground">
                  {college.name} • {degree} • {branch}
                </p>
              </div>
              <AlertSetupForm
                defaultEmail={userEmail}
                onSubmit={onSetAlert}
                isLoading={isSettingAlert}
              />
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};

export default CollegeDetailDialog;

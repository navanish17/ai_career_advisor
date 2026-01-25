import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { 
  Save, 
  ChevronDown, 
  ChevronUp,
  GraduationCap,
  BookOpen,
  Trophy,
  Briefcase,
  Target,
  CheckCircle2,
  Award,
  TrendingUp
} from 'lucide-react';
import type { BackwardRoadmapData } from '@/types/roadmap';

interface RoadmapTimelineProps {
  roadmapData: BackwardRoadmapData;
  source: string;
  onSave?: () => void;
  isSaving?: boolean;
  showSaveButton?: boolean;
}

const RoadmapTimeline = ({ 
  roadmapData, 
  source,
  onSave, 
  isSaving, 
  showSaveButton = true 
}: RoadmapTimelineProps) => {
  const [expandedSections, setExpandedSections] = useState<string[]>(['education', 'skills']);

  const toggleSection = (section: string) => {
    setExpandedSections(prev => 
      prev.includes(section) 
        ? prev.filter(s => s !== section)
        : [...prev, section]
    );
  };

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <Card>
        <CardHeader className="flex flex-row items-start justify-between">
          <div className="flex-1">
            <CardTitle className="flex items-center gap-2 text-2xl">
              <Target className="h-6 w-6 text-primary" />
              {roadmapData.normalized_career}
            </CardTitle>
            <p className="text-sm text-muted-foreground mt-2">
              {roadmapData.career_description}
            </p>
            <div className="flex gap-2 mt-3">
              <Badge variant="secondary">
                Source: {source === 'cache' ? 'Cached' : source === 'template' ? 'Template' : 'AI Generated'}
              </Badge>
              {roadmapData.career_category && (
                <Badge variant="outline">{roadmapData.career_category}</Badge>
              )}
              {roadmapData.confidence_score && (
                <Badge variant="outline">
                  Confidence: {(roadmapData.confidence_score * 100).toFixed(0)}%
                </Badge>
              )}
            </div>
          </div>
          {showSaveButton && onSave && (
            <Button onClick={onSave} disabled={isSaving} size="sm">
              <Save className="h-4 w-4 mr-2" />
              {isSaving ? 'Saving...' : 'Save Roadmap'}
            </Button>
          )}
        </CardHeader>
      </Card>

      {/* Stream Recommendation */}
      {roadmapData.stream_recommendation && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <GraduationCap className="h-5 w-5 text-blue-600" />
              Recommended Stream (Class 11-12)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <p className="font-semibold text-blue-900">
                {roadmapData.stream_recommendation.class_11_12}
              </p>
              <p className="text-sm text-blue-700 mt-1">
                {roadmapData.stream_recommendation.reason}
              </p>
            </div>
            {roadmapData.stream_recommendation.alternatives && (
              <div>
                <p className="text-sm font-medium mb-2">Alternatives:</p>
                <ul className="text-sm space-y-1 list-disc list-inside text-muted-foreground">
                  {roadmapData.stream_recommendation.alternatives.map((alt, i) => (
                    <li key={i}>{alt}</li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Required Education */}
      {roadmapData.required_education && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-green-600" />
              Required Education
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {roadmapData.required_education.preferred_degree && (
              <div>
                <p className="text-sm font-medium text-muted-foreground">Preferred Degree</p>
                <p className="font-semibold">{roadmapData.required_education.preferred_degree}</p>
              </div>
            )}
            {roadmapData.required_education.degree_options && (
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-2">Degree Options</p>
                <div className="space-y-2">
                  {roadmapData.required_education.degree_options.map((degree, i) => (
                    <div key={i} className="flex items-start gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5" />
                      <span className="text-sm">{degree}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Entrance Exams */}
      {roadmapData.entrance_exams && roadmapData.entrance_exams.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5 text-orange-600" />
              Entrance Exams
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4">
              {roadmapData.entrance_exams.map((exam, i) => (
                <div key={i} className="p-4 border rounded-lg">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-semibold">{exam.exam_name}</h4>
                      <p className="text-sm text-muted-foreground mt-1">{exam.for}</p>
                    </div>
                    <Badge variant={
                      exam.difficulty === 'Very High' ? 'destructive' : 
                      exam.difficulty === 'High' ? 'default' : 'secondary'
                    }>
                      {exam.difficulty}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    Prepare: {exam.when_to_prepare}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Skills Required */}
      {roadmapData.skills_required && roadmapData.skills_required.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="h-5 w-5 text-purple-600" />
              Skills Required
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {roadmapData.skills_required.map((skillItem, i) => (
                <div key={i} className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold">{skillItem.skill}</h4>
                    <Badge>{skillItem.level}</Badge>
                  </div>
                  {skillItem.description && (
                    <p className="text-sm text-muted-foreground">{skillItem.description}</p>
                  )}
                  {skillItem.languages && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {skillItem.languages.map((lang, j) => (
                        <Badge key={j} variant="outline">{lang}</Badge>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Projects to Build */}
      {roadmapData.projects_to_build && roadmapData.projects_to_build.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Briefcase className="h-5 w-5 text-indigo-600" />
              Projects to Build
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {roadmapData.projects_to_build.map((project, i) => (
                <li key={i} className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5" />
                  <span className="text-sm">{project}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Internships */}
      {roadmapData.internships && roadmapData.internships.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-teal-600" />
              Internships Roadmap
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {roadmapData.internships.map((internship, i) => (
                <div key={i} className="p-4 border rounded-lg">
                  <h4 className="font-semibold">{internship.type}</h4>
                  <div className="grid grid-cols-2 gap-2 mt-2 text-sm">
                    <div>
                      <span className="text-muted-foreground">When:</span> {internship.when}
                    </div>
                    <div>
                      <span className="text-muted-foreground">Duration:</span> {internship.duration}
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground mt-2">{internship.focus}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Certifications */}
      {roadmapData.certifications && roadmapData.certifications.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="h-5 w-5 text-amber-600" />
              Recommended Certifications
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3">
              {roadmapData.certifications.map((cert, i) => (
                <div key={i} className="p-3 border rounded-lg">
                  <p className="font-medium">{cert.name}</p>
                  <p className="text-sm text-muted-foreground">Provider: {cert.provider}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Top Colleges */}
      {roadmapData.top_colleges && roadmapData.top_colleges.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <GraduationCap className="h-5 w-5 text-blue-600" />
              Top Colleges
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {roadmapData.top_colleges.map((college, i) => (
                <div key={i} className="p-4 border rounded-lg">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-semibold">{college.name}</h4>
                      <p className="text-sm text-muted-foreground">Admission via: {college.admission_via}</p>
                    </div>
                    <div className="text-right">
                      <Badge variant={college.type === 'Government' ? 'default' : 'secondary'}>
                        {college.type}
                      </Badge>
                      {(college.nirf_rank_engineering || college.nirf_rank_university) && (
                        <p className="text-xs text-muted-foreground mt-1">
                          NIRF Rank: {college.nirf_rank_engineering || college.nirf_rank_university}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Career Prospects */}
      {roadmapData.career_prospects && (
        <Card className="border-primary/50 bg-primary/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Trophy className="h-5 w-5 text-primary" />
              Career Prospects
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {roadmapData.career_prospects.entry_level_salary_range_lpa && (
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="text-xs text-muted-foreground">Entry Level</p>
                  <p className="font-semibold">{roadmapData.career_prospects.entry_level_salary_range_lpa}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Mid Level</p>
                  <p className="font-semibold">{roadmapData.career_prospects.mid_level_salary_range_lpa}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Senior Level</p>
                  <p className="font-semibold">{roadmapData.career_prospects.senior_level_salary_range_lpa}</p>
                </div>
              </div>
            )}
            {roadmapData.career_prospects.growth_potential && (
              <div>
                <p className="text-sm font-medium">Growth Potential</p>
                <p className="text-sm text-muted-foreground">{roadmapData.career_prospects.growth_potential}</p>
              </div>
            )}
            {roadmapData.career_prospects.specializations && (
              <div>
                <p className="text-sm font-medium mb-2">Specializations</p>
                <div className="flex flex-wrap gap-2">
                  {roadmapData.career_prospects.specializations.map((spec, i) => (
                    <Badge key={i} variant="outline">{spec}</Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Timeline */}
      {roadmapData.timeline && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5 text-primary" />
              Your Journey Timeline
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 pl-6 border-l-2 border-primary/30">
              {Object.entries(roadmapData.timeline).map(([phase, data]) => (
                <Collapsible
                  key={phase}
                  open={expandedSections.includes(phase)}
                  onOpenChange={() => toggleSection(phase)}
                >
                  <div className="relative">
                    <div className="absolute -left-[calc(1.5rem+5px)] w-3 h-3 rounded-full bg-primary" />
                    <div className="p-4 border rounded-lg bg-card">
                      <CollapsibleTrigger className="w-full">
                        <div className="flex items-center justify-between">
                          <h4 className="font-semibold capitalize text-left">
                            {phase.replace(/_/g, ' ')}
                          </h4>
                          {expandedSections.includes(phase) ? (
                            <ChevronUp className="h-4 w-4" />
                          ) : (
                            <ChevronDown className="h-4 w-4" />
                          )}
                        </div>
                      </CollapsibleTrigger>
                      <CollapsibleContent className="mt-3 space-y-3">
                        <div>
                          <p className="text-sm font-medium text-muted-foreground">Focus</p>
                          <p className="text-sm">{data.focus}</p>
                        </div>
                        {data.exam_focus && (
                          <div>
                            <p className="text-sm font-medium text-muted-foreground">Exams</p>
                            <p className="text-sm">{data.exam_focus}</p>
                          </div>
                        )}
                        <div>
                          <p className="text-sm font-medium text-muted-foreground mb-2">Action Items</p>
                          <ul className="space-y-1">
                            {data.action_items.map((item, i) => (
                              <li key={i} className="flex items-start gap-2 text-sm">
                                <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                                <span>{item}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </CollapsibleContent>
                    </div>
                  </div>
                </Collapsible>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default RoadmapTimeline;

import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import { ThemeProvider } from "@/components/theme-provider";
import ProtectedRoute from "@/components/ProtectedRoute";

// Pages
import Home from "./pages/Home";
import Login from "./pages/auth/Login";
import Signup from "./pages/auth/Signup";
import Onboarding from "./pages/onboarding/Onboarding";
import NotFound from "./pages/NotFound";

// Career Explorer Pages
import Quiz from "./pages/career/Quiz";
import Degrees from "./pages/career/Degrees";
import Branches from "./pages/career/Branches";
import Careers from "./pages/career/Careers";

// Roadmap Pages
import RoadmapHub from "./pages/roadmap/RoadmapHub";
import ForwardPlanner from "./pages/roadmap/ForwardPlanner";
import BackwardPlanner from "./pages/roadmap/BackwardPlanner";
import MyRoadmaps from "./pages/roadmap/MyRoadmaps";
import ViewRoadmap from "./pages/roadmap/ViewRoadmap";
import SharedRoadmapView from "./pages/roadmap/SharedRoadmapView";

// College Finder Pages
import CollegeFinder from "./pages/college/collegefinder";
import MyAlerts from "./pages/college/myalert";

// Career Finder (Recommendations)
import CareerFinder from "./pages/CareerFinder";

const queryClient = new QueryClient();

const App = () => (
  <ThemeProvider defaultTheme="light" storageKey="ai-career-pilot-theme">
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <TooltipProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <Routes>
              {/* Public Routes */}
              <Route path="/auth/login" element={<Login />} />
              <Route path="/auth/signup" element={<Signup />} />

              {/* Onboarding - requires auth but not onboarding completion */}
              <Route
                path="/onboarding"
                element={
                  <ProtectedRoute requireOnboarding={false}>
                    <Onboarding />
                  </ProtectedRoute>
                }
              />
              {/* Public Roadmap View */}
              <Route path="/roadmap/shared/:token" element={<SharedRoadmapView />} />

              {/* Protected Routes */}
              {/* Protected Routes */}
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <Home />
                  </ProtectedRoute>
                }
              />

              {/* Career Explorer Routes */}
              <Route
                path="/quiz"
                element={
                  <ProtectedRoute>
                    <Quiz />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/stream-finder"
                element={
                  <ProtectedRoute>
                    <Quiz />
                  </ProtectedRoute>
                }
              />
              {/* Redirect legacy /college links to /college-finder */}
              <Route path="/college" element={<Navigate to="/college-finder" replace />} />
              <Route
                path="/degrees"
                element={
                  <ProtectedRoute>
                    <Degrees />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/branches/:degreeId"
                element={
                  <ProtectedRoute>
                    <Branches />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/careers/:branchId"
                element={
                  <ProtectedRoute>
                    <Careers />
                  </ProtectedRoute>
                }
              />

              {/* Roadmap Routes */}
              <Route
                path="/roadmap"
                element={
                  <ProtectedRoute>
                    <RoadmapHub />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/roadmap/forward"
                element={
                  <ProtectedRoute>
                    <ForwardPlanner />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/roadmap/backward"
                element={
                  <ProtectedRoute>
                    <BackwardPlanner />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/roadmap/my-roadmaps"
                element={
                  <ProtectedRoute>
                    <MyRoadmaps />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/roadmap/view/:id"
                element={
                  <ProtectedRoute>
                    <ViewRoadmap />
                  </ProtectedRoute>
                }
              />

              {/* College Finder Routes */}
              <Route
                path="/college-finder"
                element={
                  <ProtectedRoute>
                    <CollegeFinder />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/my-alerts"
                element={
                  <ProtectedRoute>
                    <MyAlerts />
                  </ProtectedRoute>
                }
              />

              {/* Career Finder Route */}
              <Route
                path="/career-finder"
                element={
                  <ProtectedRoute>
                    <CareerFinder />
                  </ProtectedRoute>
                }
              />

              {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </BrowserRouter>
        </TooltipProvider>
      </AuthProvider>
    </QueryClientProvider>
  </ThemeProvider>
);

export default App;

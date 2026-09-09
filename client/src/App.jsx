import { lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";

import { RootLayout } from "./components/layout/RootLayout";
import { ProtectedRoute } from "./components/layout/ProtectedRoute";
import { SectionLoader } from "./components/common/Loader";

const Home = lazy(() => import("./pages/Home"));
const GigsBrowse = lazy(() => import("./pages/GigsBrowse"));
const GigDetail = lazy(() => import("./pages/GigDetail"));
const PostGig = lazy(() => import("./pages/PostGig"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const Notifications = lazy(() => import("./pages/Notifications"));
const Profile = lazy(() => import("./pages/Profile"));
const Login = lazy(() => import("./pages/Login"));
const Register = lazy(() => import("./pages/Register"));
const About = lazy(() => import("./pages/About"));
const Contact = lazy(() => import("./pages/Contact"));
const ThankYou = lazy(() => import("./pages/ThankYou"));
const Privacy = lazy(() => import("./pages/Privacy"));
const Terms = lazy(() => import("./pages/Terms"));
const NotFound = lazy(() => import("./pages/NotFound"));

export default function App() {
  return (
    <Suspense fallback={<SectionLoader label="Loading Soko Comrada…" />}>
      <Routes>
        <Route element={<RootLayout />}>
          <Route index element={<Home />} />
          <Route path="gigs" element={<GigsBrowse />} />
          <Route path="gigs/:gigId" element={<GigDetail />} />
          <Route path="users/:userId" element={<Profile />} />
          <Route path="login" element={<Login />} />
          <Route path="register" element={<Register />} />
          <Route path="about" element={<About />} />
          <Route path="contact" element={<Contact />} />
          <Route path="thank-you" element={<ThankYou />} />
          <Route path="privacy" element={<Privacy />} />
          <Route path="terms" element={<Terms />} />

          <Route element={<ProtectedRoute />}>
            <Route path="gigs/new" element={<PostGig />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="notifications" element={<Notifications />} />
          </Route>

          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </Suspense>
  );
}
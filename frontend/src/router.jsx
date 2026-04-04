import { Routes, Route } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Upload from "./pages/Upload";
import Notes from "./pages/Notes";
import Search from "./pages/Search";
import Login from "./pages/Login";

export default function Router() {
  return (
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/notes/:id" element={<Notes />} />
        <Route path="/search" element={<Search />} />
        <Route path="/login" element={<Login />} />
      </Routes>
  );
}
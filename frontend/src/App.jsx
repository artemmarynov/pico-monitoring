import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Header from "./components/Header";
import Dashboard from "./pages/Dashboard";
import "./styles/base.css";
import "./styles/header.css";
import "./styles/dashboard.css";

export default function App() {
  return <BrowserRouter>
    <Header />
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  </BrowserRouter>;
}

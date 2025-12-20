import { BrowserRouter, Routes, Route } from "react-router-dom";

import Header from "./components/Header";
import "./styles.css"
import Home from "./pages/Home";
import About from "./pages/About";
import Contacts from "./pages/Contacts";
import AdminLogin from "./pages/AdminLogin";

import AdminLayout from "./pages/AdminLayout";
import AdminHome from "./pages/AdminHome";
import AdminModels from "./pages/AdminModels";
import AdminPerformance from "./pages/AdminPerformance";
import AdminMisc from "./pages/AdminMisc";

function App() {
  return (
    <BrowserRouter>
      <Header />

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/contacts" element={<Contacts />} />

        <Route path="/admin/login" element={<AdminLogin />} />

        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<AdminHome />} />
          <Route path="models" element={<AdminModels />} />
          <Route path="performance" element={<AdminPerformance />} />
          <Route path="misk" element={<AdminMisc />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;

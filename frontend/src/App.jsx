import { BrowserRouter, Routes, Route } from "react-router-dom";

import Header from "./components/Header";
import "./styles.css"
import AdminLogin from "./pages/AdminLogin";
import AdminLayout from "./pages/AdminLayout";
import AdminPerformance from "./pages/AdminPerformance";
import AdminMisc from "./pages/AdminMisc";
import About from "./pages/About";
import Contacts from "./pages/Contacts";

function App() {
  return (
    <BrowserRouter>
      <Header />

      <Routes>
        {/* Public pages */}
        <Route path="/about" element={<About />} />
        <Route path="/contacts" element={<Contacts />} />

        {/* Login (kept on both paths so existing links continue to work) */}
        <Route path="/" element={<AdminLogin />} />
        <Route path="/admin/login" element={<AdminLogin />} />

        {/* Admin area (layout provides the sidebar via <Outlet />) */}
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<AdminPerformance />} />
          <Route path="performance" element={<AdminPerformance />} />
          <Route path="misk" element={<AdminMisc />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;

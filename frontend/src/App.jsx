import { BrowserRouter, Routes, Route } from "react-router-dom";

import Header from "./components/Header";
import "./styles.css";
import "./index.css";
import "./App.css";
import AdminLogin from "./pages/AdminLogin";
import AdminLayout from "./pages/AdminLayout";
import AdminPerformance from "./pages/AdminPerformance";
import AdminMisc from "./pages/AdminMisc";
import About from "./pages/About";
import Contacts from "./pages/Contacts";

import { AuthProvider } from "./context/AuthContext";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Header />

        <Routes>
          {/* Public pages */}
          <Route path="/about" element={<About />} />
          <Route path="/contacts" element={<Contacts />} />

          {/* Login */}
          <Route path="/" element={<AdminLogin />} />
          <Route path="/admin/login" element={<AdminLogin />} />

          {/* Admin area */}
          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<AdminPerformance />} />
            <Route path="performance" element={<AdminPerformance />} />
            <Route path="misc" element={<AdminMisc />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;

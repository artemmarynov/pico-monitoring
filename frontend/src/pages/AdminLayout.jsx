import AdminSidebar from "../components/AdminSidebar";
import { Outlet, Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function AdminLayout() {
  const { loading, isAdmin } = useAuth();

  if (loading) return null;
  if (!isAdmin) return <Navigate to="/admin/login" replace />;

  return (
    <main className="admin-page">
      <AdminSidebar />
      <section className="admin-content">
        <Outlet />
      </section>
    </main>
  );
}

export default AdminLayout;

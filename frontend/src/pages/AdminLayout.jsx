import AdminSidebar from "../components/AdminSidebar";
import { Outlet } from "react-router-dom";

function AdminLayout() {
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

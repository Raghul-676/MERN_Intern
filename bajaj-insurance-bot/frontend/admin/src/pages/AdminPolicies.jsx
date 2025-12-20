// frontend/admin/src/pages/AdminPolicies.jsx
import React, { useEffect, useState } from "react";
import { api } from "../api/client";

export default function AdminPolicies() {
  const [form, setForm] = useState({
    insurance_type: "Health",
    policy_name: "",
    policy_year: "",
    document_url: "",
    publish: false,
  });

  const [policies, setPolicies] = useState([]);

  const loadPolicies = async () => {
    try {
      const res = await api.get("/admin/policies");
      const data = res.data;
      // if backend returns array directly
      setPolicies(Array.isArray(data) ? data : []);
      // if later you change backend to `{ policies: [...] }`, then use:
      // setPolicies(Array.isArray(data.policies) ? data.policies : []);
    } catch (e) {
      console.error("Failed to load policies", e);
      setPolicies([]);
    }
  };

  useEffect(() => {
    loadPolicies();
  }, []);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((f) => ({ ...f, [name]: type === "checkbox" ? checked : value }));
  };

const handleSubmit = async (e) => {
  e.preventDefault();
  console.log("Submitting form", form);
  try {
    await api.post("/admin/policies", form);
    await loadPolicies();
  } catch (err) {
    console.error("Upload failed", err.response?.data || err.message);
  }
};

  const togglePublish = async (id, published) => {
    await api.patch(`/admin/policies/${id}`, { published: !published });
    await loadPolicies();
  };

  return (
    <div style={{ padding: "1rem" }}>
      <h2>Admin – Manage Policies</h2>

      <form onSubmit={handleSubmit} style={{ marginBottom: "1rem" }}>
        <select
          name="insurance_type"
          value={form.insurance_type}
          onChange={handleChange}
        >
          <option>Health</option>
          <option>Motor</option>
          <option>Travel</option>
        </select>

        <input
          name="policy_name"
          placeholder="Policy Name"
          value={form.policy_name}
          onChange={handleChange}
        />

        <input
          name="policy_year"
          placeholder="Policy Year"
          value={form.policy_year}
          onChange={handleChange}
        />

        <input
          name="document_url"
          placeholder="Policy PDF URL"
          value={form.document_url}
          onChange={handleChange}
        />

        <label>
          <input
            type="checkbox"
            name="publish"
            checked={form.publish}
            onChange={handleChange}
          />
          Publish
        </label>

        <button type="submit">Upload & Process</button>
      </form>

      <h3>Existing Policies</h3>
      <table border="1" cellPadding="4">
        <thead>
          <tr>
            <th>Type</th>
            <th>Name</th>
            <th>Year</th>
            <th>Published</th>
            <th>Toggle</th>
          </tr>
        </thead>
        <tbody>
          {Array.isArray(policies) &&
            policies.map((p) => (
              <tr key={p.id}>
                <td>{p.insurance_type}</td>
                <td>{p.policy_name}</td>
                <td>{p.policy_year}</td>
                <td>{p.published ? "Yes" : "No"}</td>
                <td>
                  <button onClick={() => togglePublish(p.id, p.published)}>
                    {p.published ? "Unpublish" : "Publish"}
                  </button>
                </td>
              </tr>
            ))}
        </tbody>
      </table>
    </div>
  );
}

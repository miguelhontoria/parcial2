const API_URL = "https://parcial2-82eb.onrender.com";
const CLOUD_NAME = "dundnn1ge";
const UPLOAD_PRESET = "preset_mapa";

const map = L.map("map").setView([40.4168, -3.7038], 5);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors",
}).addTo(map);

let currentMarkers = [];

function clearMarkers() {
  currentMarkers.forEach((m) => map.removeLayer(m));
  currentMarkers = [];
}

async function obtenerCorreoSesion() {
  const res = await fetch(`${API_URL}/auth/sesion`, {
    credentials: "include",
  });
  const data = await res.json();
  return data.correo;
}

async function cargarReseñas() {
  const res = await fetch(`${API_URL}/reseñas`, {
    credentials: "include",
  });
  const data = await res.json();
  const tbody = document.querySelector("#reseñasTable tbody");
  tbody.innerHTML = "";
  clearMarkers();

  data.reseñas.forEach((r) => {
    const tr = document.createElement("tr");

    const direccionLink = `<a href="#" class="direccion-link" data-direccion="${r.direccion}">${r.direccion}</a>`;

    tr.innerHTML = `
      <td>${r.establecimiento}</td>
      <td>${direccionLink}</td>
      <td>${r.latitud}</td>
      <td>${r.longitud}</td>
      <td>${r.valoracion}</td>
    `;
    tbody.appendChild(tr);

    const marker = L.marker([r.latitud, r.longitud]).addTo(map);
    marker.bindPopup(
      `<b>${r.establecimiento}</b><br>${r.direccion}<br>Valoración: ${r.valoracion}`
    );
    currentMarkers.push(marker);
  });

  document.querySelectorAll(".direccion-link").forEach((link) => {
    link.addEventListener("click", async (e) => {
      e.preventDefault();
      const direccion = e.target.getAttribute("data-direccion");
      const detalleRes = await fetch(
        `${API_URL}/reseñas/${encodeURIComponent(direccion)}`,
        { credentials: "include" }
      );
      const detalle = await detalleRes.json();

      if (!detalleRes.ok) {
        alert("No se pudo obtener el detalle de la reseña.");
        return;
      }

      const imagenesHTML =
        Array.isArray(detalle.imagenes) && detalle.imagenes.length > 0
          ? detalle.imagenes
              .map(
                (url) =>
                  `<img src="${url}" width="120" style="margin:5px; border-radius:4px;">`
              )
              .join("")
          : "Sin imágenes";

      const popupHTML = `
        <strong>Establecimiento:</strong> ${detalle.establecimiento}<br>
        <strong>Dirección:</strong> ${detalle.direccion}<br>
        <strong>Autor:</strong> ${detalle.nombre_autor} (${detalle.correo_autor})<br>
        <strong>Token OAuth:</strong> ${detalle.token_oauth}<br>
        <strong>Emisión:</strong> ${detalle.token_emision}<br>
        <strong>Caducidad:</strong> ${detalle.token_caducidad}<br>
        <strong>Imágenes:</strong><br>${imagenesHTML}
      `;

      const popupWindow = window.open(
        "",
        "Detalle Reseña",
        "width=600,height=700"
      );
      popupWindow.document.write(
        `<html><head><title>Detalle de reseña</title></head><body style="font-family:sans-serif;padding:20px;">${popupHTML}</body></html>`
      );
    });
  });
}

async function initUI() {
  const correo = await obtenerCorreoSesion();

  const loginBtn = document.getElementById("loginBtn");
  const logoutBtn = document.getElementById("logoutBtn");
  const reseñaForm = document.getElementById("reseñaForm");
  const tablaReseñas = document.getElementById("tablaReseñas");
  const mapDiv = document.getElementById("map");
  const mensajeLogin = document.getElementById("mensajeLogin");

  reseñaForm.style.display = "none";
  tablaReseñas.style.display = "none";
  mapDiv.style.display = "none";
  mensajeLogin.textContent = "";

  if (!correo) {
    loginBtn.style.display = "inline-block";
    logoutBtn.style.display = "none";
    reseñaForm.style.display = "none";
    mensajeLogin.textContent = "Debes iniciar sesión para ver las reseñas.";
    return;
  }

  loginBtn.style.display = "none";
  logoutBtn.style.display = "inline-block";
  reseñaForm.style.display = "flex";
  tablaReseñas.style.display = "block";
  mapDiv.style.display = "block";
  mensajeLogin.textContent = `Usuario: ${correo}`;

  await cargarReseñas();
  setTimeout(() => {
    map.invalidateSize();
  }, 300);
}

window.addEventListener("DOMContentLoaded", initUI);

document.getElementById("loginBtn").addEventListener("click", () => {
  window.location.href = `${API_URL}/auth/google/login`;
});

document.getElementById("logoutBtn").addEventListener("click", async () => {
  await fetch(`${API_URL}/auth/logout`, {
    method: "POST",
    credentials: "include",
  });

  alert("Sesión cerrada");
  await initUI();
});

document.getElementById("reseñaForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const establecimiento = document
    .getElementById("establecimiento")
    .value.trim();
  const direccion = document.getElementById("direccion").value.trim();
  const valoracion = document.getElementById("valoracion").value.trim();
  const imagen = document.getElementById("imagen").files[0];
  const correo = await obtenerCorreoSesion();

  if (!correo || !establecimiento || !direccion || !valoracion) {
    alert("Faltan datos o no hay sesión activa.");
    return;
  }

  let imagenURI = null;
  if (imagen) {
    const formData = new FormData();
    formData.append("file", imagen);
    formData.append("upload_preset", UPLOAD_PRESET);

    const cloudinaryURL = `https://api.cloudinary.com/v1_1/${CLOUD_NAME}/image/upload`;
    const cloudRes = await fetch(cloudinaryURL, {
      method: "POST",
      body: formData,
    });
    const cloudData = await cloudRes.json();

    if (!cloudRes.ok || !cloudData.secure_url) {
      alert("No se pudo subir la imagen.");
      return;
    }
    imagenURI = cloudData.secure_url;
  }

  const formDataBackend = new FormData();
  formDataBackend.append("establecimiento", establecimiento);
  formDataBackend.append("direccion", direccion);
  formDataBackend.append("valoracion", valoracion);
  if (imagen) formDataBackend.append("imagen", imagen);

  const res = await fetch(`${API_URL}/reseñas`, {
    method: "POST",
    body: formDataBackend,
    credentials: "include",
  });

  const data = await res.json();
  if (!res.ok) {
    alert("No se pudo guardar la reseña.");
    return;
  }

  alert("Reseña añadida correctamente.");
  await cargarReseñas();
});

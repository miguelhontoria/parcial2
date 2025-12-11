let map;
let currentUserEmail = null;
let currentMarkers = [];

// Inicializar mapa
function initMap() {
  map = L.map("map").setView([40.4168, -3.7038], 5);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap contributors",
  }).addTo(map);
}

// Limpiar marcadores previos
function clearMarkers() {
  currentMarkers.forEach((m) => map.removeLayer(m));
  currentMarkers = [];
}

// Mostrar u ocultar elementos según sesión
function actualizarUI() {
  const loginBtn = document.getElementById("loginBtn");
  const logoutBtn = document.getElementById("logoutBtn");
  const marcadorForm = document.getElementById("marcadorForm");
  const mapaTitulo = document.getElementById("mapTitle");

  if (currentUserEmail) {
    loginBtn.style.display = "none";
    logoutBtn.style.display = "inline-block";
    marcadorForm.style.display = "flex";
    mapaTitulo.textContent = `Mapa de: ${currentUserEmail}`;
    mapaTitulo.style.display = "block";
  } else {
    loginBtn.style.display = "inline-block";
    logoutBtn.style.display = "none";
    marcadorForm.style.display = "none";
    mapaTitulo.style.display = "none";
  }
}

// Renderizar marcadores
function renderMarkers(marcadores) {
  clearMarkers();
  marcadores.forEach((m) => {
    const lat = parseFloat(m.latitud);
    const lon = parseFloat(m.longitud);
    if (!isNaN(lat) && !isNaN(lon)) {
      const marker = L.marker([lat, lon]).addTo(map);
      let popupContent = `<b>${m.ciudad}</b>`;
      if (m.url_imagen) {
        popupContent += `<br><img src="${m.url_imagen}" width="100">`;
      }
      marker.bindPopup(popupContent);
      currentMarkers.push(marker);
    }
  });
}

// Verificar sesión y cargar marcadores
async function checkSession() {
  const resp = await fetch("/auth/sesion");
  if (resp.ok) {
    const data = await resp.json();
    if (data.correo) {
      currentUserEmail = data.correo;
      actualizarUI();
      const res = await fetch(`/usuarios/${currentUserEmail}/marcadores`);
      if (res.ok) {
        const datos = await res.json();
        renderMarkers(datos.marcadores);
      }
    } else {
      actualizarUI();
    }
  }
}

// Login
document.getElementById("loginBtn").addEventListener("click", () => {
  window.location.href = "/auth/google/login";
});

// Logout
document.getElementById("logoutBtn").addEventListener("click", async () => {
  const resp = await fetch("/auth/logout", { method: "POST" });
  if (resp.ok) {
    currentUserEmail = null;
    actualizarUI();
    clearMarkers();
  }
});

// Añadir marcador
document
  .getElementById("marcadorForm")
  .addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!currentUserEmail) return;

    const ciudad = document.getElementById("ciudad").value;
    const imagen = document.getElementById("imagen").files[0];

    const formData = new FormData();
    formData.append("ciudad", ciudad);
    if (imagen) formData.append("imagen", imagen);

    const resp = await fetch(`/usuarios/${currentUserEmail}/marcadores`, {
      method: "POST",
      body: formData,
    });

    if (resp.ok) {
      const res = await fetch(`/usuarios/${currentUserEmail}/marcadores`);
      if (res.ok) {
        const datos = await res.json();
        renderMarkers(datos.marcadores);
      }
    } else {
      alert("Error al añadir marcador");
    }
  });

// Visitar otro mapa
document.getElementById("visitBtn").addEventListener("click", async () => {
  const email = document.getElementById("visitEmail").value;
  if (!email) return;
  const resp = await fetch(`/usuarios/${email}/marcadores`);
  if (resp.ok) {
    const data = await resp.json();
    renderMarkers(data.marcadores);
    document.getElementById("mapTitle").textContent = `Mapa de: ${email}`;
    document.getElementById("mapTitle").style.display = "block";
  }
});

// Inicializar
initMap();
checkSession();

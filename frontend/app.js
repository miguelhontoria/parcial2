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
  const res = await fetch("http://127.0.0.1:8000/auth/sesion", {
    credentials: "include",
  });
  const data = await res.json();
  return data.correo;
}

// Inicializa la UI según si hay sesión o no
async function initUI() {
  const correo = await obtenerCorreoSesion();
  const loginBtn = document.getElementById("loginBtn");
  const logoutBtn = document.getElementById("logoutBtn");
  const marcadorForm = document.getElementById("marcadorForm");

  clearMarkers();
  const titulo = document.getElementById("correoTitulo");
  if (titulo) titulo.remove();

  // Elimina avisos previos
  const oldAvisos = document.querySelectorAll("p[data-aviso='login']");
  oldAvisos.forEach((p) => p.remove());

  if (!correo) {
    // Estado sin sesión
    loginBtn.style.display = "inline-block";
    logoutBtn.style.display = "none";
    marcadorForm.style.display = "none";

    const aviso = document.createElement("p");
    aviso.textContent = "Debes iniciar sesión para añadir marcadores.";
    aviso.setAttribute("data-aviso", "login");
    document.body.insertBefore(aviso, document.getElementById("map"));
    return;
  }

  // Estado con sesión
  loginBtn.style.display = "none";
  logoutBtn.style.display = "inline-block";
  marcadorForm.style.display = "block";

  const h2 = document.createElement("h2");
  h2.id = "correoTitulo";
  h2.textContent = `Mapa de: ${correo}`;
  document.body.insertBefore(h2, document.getElementById("map"));

  const res = await fetch(`http://127.0.0.1:8000/usuarios/${correo}`);
  const usuario = await res.json();
  if (usuario.marcadores) {
    usuario.marcadores.forEach(({ ciudad, latitud, longitud, imagenURI }) => {
      const marker = L.marker([latitud, longitud]).addTo(map);
      marker.bindPopup(
        `<b>${ciudad}</b><br>${
          imagenURI ? `<img src="${imagenURI}" width="100">` : ""
        }`
      );
      currentMarkers.push(marker);
    });
  }
}

window.addEventListener("DOMContentLoaded", initUI);

document.getElementById("loginBtn").addEventListener("click", () => {
  window.location.href = "http://127.0.0.1:8000/auth/google/login";
});

document.getElementById("logoutBtn").addEventListener("click", async () => {
  await fetch("http://127.0.0.1:8000/auth/logout", {
    method: "POST",
    credentials: "include",
  });

  alert("Sesión cerrada");

  // Reinicializa la UI sin necesidad de F5
  await initUI();
});

document
  .getElementById("marcadorForm")
  .addEventListener("submit", async (e) => {
    e.preventDefault();

    const ciudad = document.getElementById("ciudad").value.trim();
    const imagen = document.getElementById("imagen").files[0];
    const correo = await obtenerCorreoSesion();

    if (!correo || !ciudad || !imagen) {
      alert("Faltan datos o no hay sesión activa.");
      return;
    }

    const formData = new FormData();
    formData.append("file", imagen);
    formData.append("upload_preset", UPLOAD_PRESET);

    const cloudinaryURL = `https://api.cloudinary.com/v1_1/${CLOUD_NAME}/image/upload`;
    const cloudRes = await fetch(cloudinaryURL, {
      method: "POST",
      body: formData,
    });
    const cloudData = await cloudRes.json();
    console.log("Cloudinary response:", cloudData);

    if (!cloudRes.ok || !cloudData.secure_url) {
      alert("No se pudo subir la imagen. Revisa cloud_name y upload_preset.");
      return;
    }

    const imagenURI = cloudData.secure_url;

    const geoRes = await fetch(
      `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(
        ciudad
      )}`,
      {
        headers: {
          "User-Agent": "MiMapa/1.0 (mailto:miguelhontoria03@gmail.com)",
        },
      }
    );
    const geoData = await geoRes.json();
    if (!geoData[0]) {
      alert("No se pudo geolocalizar la ciudad.");
      return;
    }
    const latitud = parseFloat(geoData[0].lat);
    const longitud = parseFloat(geoData[0].lon);

    const marcador = { ciudad, latitud, longitud, imagenURI };
    const res = await fetch(
      `http://127.0.0.1:8000/usuarios/${correo}/marcadores`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(marcador),
      }
    );

    const data = await res.json();
    if (!res.ok) {
      alert("No se pudo guardar el marcador.");
      return;
    }

    alert("Marcador añadido correctamente.");
    window.location.reload();
  });

document.getElementById("visitBtn").addEventListener("click", async () => {
  const visitEmail = document.getElementById("visitEmail").value.trim();
  if (!visitEmail) {
    alert("Introduce un email para visitar su mapa.");
    return;
  }

  const res = await fetch(
    `http://127.0.0.1:8000/usuarios/${visitEmail}/visitar`,
    { credentials: "include" }
  );
  const data = await res.json();

  if (data.error) {
    alert(data.error);
    return;
  }

  clearMarkers();

  if (data.marcadores && data.marcadores.length > 0) {
    data.marcadores.forEach(({ ciudad, latitud, longitud, imagenURI }) => {
      const marker = L.marker([latitud, longitud]).addTo(map);
      marker.bindPopup(
        `<b>${ciudad}</b><br>${
          imagenURI ? `<img src="${imagenURI}" width="100">` : ""
        }`
      );
      currentMarkers.push(marker);
    });

    const first = data.marcadores[0];
    map.setView([first.latitud, first.longitud], 8);
  }
});

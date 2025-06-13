// Theme toggle
document.getElementById('toggle-theme').addEventListener('change', () => {
    document.body.classList.toggle('dark-theme');
});

// Daily Quote
const quotes = [
    "Content is fire, social media is gasoline.",
    "The best marketing doesn’t feel like marketing.",
    "Write drunk, edit sober. – Hemingway",
    "Don't optimize for conversions, optimize for experience.",
    "Make it simple. Make it memorable.",
    "Your first draft won’t be perfect — just write.",
    "SEO is the new storefront window.",
    "Creativity is intelligence having fun."
];
const dayIndex = new Date().getDate() % quotes.length;
document.getElementById('daily-quote').innerText = quotes[dayIndex];

// Particles
particlesJS("particles-js", {
    particles: {
        number: { value: 60, density: { enable: true, value_area: 800 } },
        color: { value: "#333333" },
        shape: { type: "circle" },
        opacity: { value: 0.3, random: true },
        size: { value: 3, random: true },
        move: { enable: true, speed: 1 }
    },
    interactivity: {
        detect_on: "canvas",
        events: { onhover: { enable: true, mode: "repulse" } },
        modes: { repulse: { distance: 100 } }
    },
    retina_detect: true
});

// Time
function updateTime() {
    const timeElem = document.getElementById('local-time');
    const now = new Date();
    timeElem.innerText = `Local Time: ${now.toLocaleTimeString()}`;
}
setInterval(updateTime, 1000);
updateTime();

// Geo + Weather
navigator.geolocation.getCurrentPosition(
    success => {
        const lat = success.coords.latitude;
        const lon = success.coords.longitude;

        const apiKey = 'cd5c22536e6c74ca9a050427fbb3abe9';

        fetch(`https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${apiKey}&units=metric`)
          .then(w => w.json())
          .then(w => {
            const temp = w.main.temp;
            const icon = w.weather[0].icon;
            document.getElementById('weather').innerHTML =
              `Weather: <img src="https://openweathermap.org/img/wn/${icon}.png"> ${temp}°C`;
          });

        fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`)
          .then(r => r.json())
          .then(r => {
            console.log("Reverse geocode response:", r); // 👈 log for debugging
            const city = r.address.city || r.address.town || r.address.village || 'your location';
            const hour = new Date().getHours();
            let greeting = hour < 12 ? "Good Morning" : hour < 18 ? "Good Afternoon" : "Good Evening";
            document.getElementById('greeting-text').innerText = `${greeting}, visitor from ${city}!`;
          });
    },
    error => {
        console.error("Geolocation error:", error);
        document.getElementById('greeting-text').innerText = "Hello! We couldn't get your exact location.";
    }
);

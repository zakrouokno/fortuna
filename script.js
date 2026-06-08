const tg = window.Telegram.WebApp;
tg.expand();

const urlParams = new URLSearchParams(window.location.search);
const userId = urlParams.get('user_id');
if (userId) {
    document.getElementById('user-id').innerText = userId;
}

const canvas = document.getElementById('wheel');
const ctx = canvas.getContext('2d');
const spinBtn = document.getElementById('spin-btn');
const modal = document.getElementById('win-modal');
const claimBtn = document.getElementById('claim-btn');

// Строгие, аккуратные названия без смайлов
const prizes = [
    "50 Free Spins",
    "💥 MEGA BONUS 💥",
    "100 Free Spins",
    "10 Free Spins",
    "🔥 SUPER BONUS 🔥",
    "25 Free Spins"
];

// Премиальная темная палитра для секторов
const colors = ["#1b1e27", "#14161d", "#1b1e27", "#14161d", "#1b1e27", "#14161d"];
const numSectors = prizes.length;
const arc = 2 * Math.PI / numSectors;

let startAngle = 0;
let isSpinning = false;

function drawWheel() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const radius = canvas.width / 2;
    const center = radius;

    for (let i = 0; i < numSectors; i++) {
        const angle = startAngle + i * arc;
        ctx.fillStyle = colors[i];
        
        ctx.beginPath();
        ctx.moveTo(center, center);
        ctx.arc(center, center, radius - 5, angle, angle + arc);
        ctx.lineTo(center, center);
        ctx.fill();
        
        // Разделительные линии секторов (аккуратные, темно-серые)
        ctx.strokeStyle = "#222530";
        ctx.lineWidth = 2;
        ctx.stroke();

        // Текст на секторах
        ctx.save();
        ctx.fillStyle = "#a3a7b5"; // Матовый белый/серый цвет для обычного текста
        
        // Подсвечиваем главный выигрыш неоновым цветом
        if (prizes[i].includes("BONUS")) {
            ctx.fillStyle = "#00f0ff";
        }
        
        ctx.translate(center, center);
        ctx.rotate(angle + arc / 2);
        ctx.textAlign = "right";
        ctx.font = "600 11px 'Inter', sans-serif";
        ctx.fillText(prizes[i], radius - 25, 4);
        ctx.restore();
    }

    // Внутреннее аккуратное кольцо
    ctx.beginPath();
    ctx.arc(center, center, 40, 0, 2 * Math.PI);
    ctx.fillStyle = "#1f222c";
    ctx.fill();
    ctx.strokeStyle = "#222530";
    ctx.stroke();
}

spinBtn.addEventListener('click', () => {
    if (isSpinning) return;
    isSpinning = true;
    spinBtn.style.opacity = '0';
    spinBtn.style.pointerEvents = 'none';

    // Скрипт по-прежнему бьет точно в цель — сектор №1 ("💥 MEGA BONUS 💥")
    const targetSector = 1; 
    const sectorAngle = (2 * Math.PI) / numSectors;
    const targetAngle = (3 * Math.PI / 2) - (targetSector * sectorAngle) - (sectorAngle / 2);
    
    const totalRotation = (2 * Math.PI * 6) + targetAngle - (startAngle % (2 * Math.PI));
    
    let currentRotation = 0;
    const duration = 4500; // Чуть более плавное и долгое кручение (4.5 сек)
    const start = performance.now();

    function animate(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        
        // Плавный Ease-out
        const easeOut = 1 - Math.pow(1 - progress, 4);
        
        startAngle = startAngle + (totalRotation * easeOut) - currentRotation;
        currentRotation = totalRotation * easeOut;
        
        drawWheel();

        if (progress < 1) {
            requestAnimationFrame(animate);
        } else {
            setTimeout(() => {
                modal.classList.add('show');
            }, 600);
        }
    }

    requestAnimationFrame(animate);
});

claimBtn.addEventListener('click', () => {
    const finalPrize = "250 FREE SPINS + 200% BONUS";
    tg.sendData(finalPrize); 
    tg.close(); 
});

drawWheel();

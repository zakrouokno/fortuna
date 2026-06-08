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

// Строгие лаконичные названия на украинском без дешевых эмодзи
const prizes = [
    "50 ВІЛЬНИХ СПІНІВ",
    "MEGA BONUS",
    "100 ВІЛЬНИХ СПІНІВ",
    "10 ВІЛЬНИХ СПІНІВ",
    "SUPER BONUS",
    "25 ВІЛЬНИХ СПІНІВ"
];

// Матовые темные оттенки для премиального монохромного вида
const colors = ["#161822", "#11131a", "#161822", "#11131a", "#161822", "#11131a"];
const numSectors = prizes.length;
const arc = 2 * Math.PI / numSectors;

let startAngle = 0;
let isSpinning = false;

function drawWheel() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const radius = canvas.width / 2;
    const center = radius;

    // 1. Рисуем секторы колеса
    for (let i = 0; i < numSectors; i++) {
        const angle = startAngle + i * arc;
        ctx.fillStyle = colors[i];
        
        ctx.beginPath();
        ctx.moveTo(center, center);
        ctx.arc(center, center, radius - 10, angle, angle + arc);
        ctx.lineTo(center, center);
        ctx.fill();
        
        // Тонкие стильные разделительные линии между секторами
        ctx.strokeStyle = "#232736";
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // 2. Рисуем текст (Принудительно задаем шрифт Inter, который подключен в HTML)
        ctx.save();
        
        // По умолчанию аккуратный приглушенный серебряный цвет текста
        ctx.fillStyle = "#8a8f9f"; 
        
        // Подсвечиваем главные выигрышные секторы неоновым цианом
        if (prizes[i].includes("BONUS")) {
            ctx.fillStyle = "#00f0ff";
        }
        
        ctx.translate(center, center);
        ctx.rotate(angle + arc / 2);
        ctx.textAlign = "right";
        
        // Ставим правильный дорогой шрифт вместо дефолтного системного
        ctx.font = "bold 11px 'Inter', sans-serif"; 
        ctx.letterSpacing = "0.5px";
        
        // Смещаем текст ближе к краю, чтобы он не налезал на центральную кнопку
        ctx.fillText(prizes[i], radius - 30, 4);
        ctx.restore();
    }

    // 3. Внешний тонкий неоновый контур всего колеса
    ctx.beginPath();
    ctx.arc(center, center, radius - 10, 0, 2 * Math.PI);
    ctx.strokeStyle = "rgba(0, 240, 255, 0.3)";
    ctx.lineWidth = 2;
    ctx.stroke();

    // 4. Центральная матовая подложка под кнопку (убираем дешевый желтый круг)
    ctx.beginPath();
    ctx.arc(center, center, 44, 0, 2 * Math.PI);
    ctx.fillStyle = "#0d0e12";
    ctx.fill();
    ctx.strokeStyle = "#1f222c";
    ctx.lineWidth = 2;
    ctx.stroke();
}

spinBtn.addEventListener('click', () => {
    if (isSpinning) return;
    isSpinning = true;
    
    // Вместо полного исчезновения делаем стильное затухание кнопки
    spinBtn.style.opacity = '0.3';
    spinBtn.style.pointerEvents = 'none';

    // Скрипт подкрутки: бьем в сектор №1 ("MEGA BONUS")
    const targetSector = 1; 
    const sectorAngle = (2 * Math.PI) / numSectors;
    const targetAngle = (3 * Math.PI / 2) - (targetSector * sectorAngle) - (sectorAngle / 2);
    
    const totalRotation = (2 * Math.PI * 6) + targetAngle - (startAngle % (2 * Math.PI));
    
    let currentRotation = 0;
    const duration = 5000; // 5 секунд — более плавное, премиальное торможение
    const start = performance.now();

    function animate(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        
        // Плавная кубическая функция замедления
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

// Небольшой хак: ждем полной загрузки шрифтов перед первой отрисовкой колеса
document.fonts.ready.then(() => {
    drawWheel();
});

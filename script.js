// Инициализация Telegram WebApp
const tg = window.Telegram.WebApp;
tg.expand(); // Расширяем аппку на весь экран

// Получаем user_id из URL (который передал наш бот)
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

// Названия секторов на колесе
const prizes = [
    "50 ФРІСПІНІВ",
    "💥 СУПЕР ПРИЗ 💥",
    "100 ФРІСПІНІВ",
    "СПРОБУЙ ЩЕ РАЗ",
    "🎁 КРАЩИЙ БОНУС 🎁",
    "20 ФРІСПІНІВ"
];

// Цвета секторов (чередуем фиолетовый и темный)
const colors = ["#2a1454", "#1a0b36", "#2a1454", "#1a0b36", "#2a1454", "#1a0b36"];
const numSectors = prizes.length;
const arc = 2 * Math.PI / numSectors;

let startAngle = 0;
let isSpinning = false;

// Отрисовка колеса на Canvas
function drawWheel() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const radius = canvas.width / 2;
    const center = radius;

    for (let i = 0; i < numSectors; i++) {
        const angle = startAngle + i * arc;
        ctx.fillStyle = colors[i];
        
        // Рисуем сектор
        ctx.beginPath();
        ctx.moveTo(center, center);
        ctx.arc(center, center, radius - 10, angle, angle + arc);
        ctx.lineTo(center, center);
        ctx.fill();
        
        // Рисуем золотую рамку секторов
        ctx.strokeStyle = "#ffd700";
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Текст сектора
        ctx.save();
        ctx.fillStyle = "#fff";
        // Выделяем золотом супер-призы
        if (prizes[i].includes("ПРИЗ") || prizes[i].includes("БОНУС")) {
            ctx.fillStyle = "#ffd700";
        }
        ctx.translate(center, center);
        ctx.rotate(angle + arc / 2);
        ctx.textAlign = "right";
        ctx.font = "bold 12px sans-serif";
        ctx.fillText(prizes[i], radius - 25, 5);
        ctx.restore();
    }

    // Внутренний золотой круг под кнопкой
    ctx.beginPath();
    ctx.arc(center, center, 45, 0, 2 * Math.PI);
    ctx.fillStyle = "#ffd700";
    ctx.fill();
}

// Запуск анимации кручения
spinBtn.addEventListener('click', () => {
    if (isSpinning) return;
    isSpinning = true;
    spinBtn.style.display = 'none'; // Прячем кнопку, чтоб не тыкали дважды

    // Скрипт ЖЕСТКОЙ ПОДКУПКИ:
    // Целимся строго в сектор №1 ("💥 СУПЕР ПРИЗ 💥")
    const targetSector = 1; 
    
    // Рассчитываем угол так, чтобы стрелка (вверху, это угол -Math.PI/2) указала на нужный сектор
    const sectorAngle = (2 * Math.PI) / numSectors;
    const targetAngle = (3 * Math.PI / 2) - (targetSector * sectorAngle) - (sectorAngle / 2);
    
    // Делаем 5 полных оборотов для красоты + выходим на нужный угол
    const totalRotation = (2 * Math.PI * 5) + targetAngle - (startAngle % (2 * Math.PI));
    
    let currentRotation = 0;
    const duration = 4000; // 4 секунды кручения
    const start = performance.now();

    function animate(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        
        // Функция замедления (Ease-out)
        const easeOut = 1 - Math.pow(1 - progress, 3);
        
        startAngle = startAngle + (totalRotation * easeOut) - currentRotation;
        currentRotation = totalRotation * easeOut;
        
        drawWheel();

        if (progress < 1) {
            requestAnimationFrame(animate);
        } else {
            // Колесо остановилось! Выводим победу
            setTimeout(() => {
                modal.classList.add('show');
            }, 500);
        }
    }

    requestAnimationFrame(animate);
});

// Когда юзер жмет финальную кнопку "Забрать бонус"
claimBtn.addEventListener('click', () => {
    const finalPrize = "250 FREE SPINS + 200% FIRST DEPOSIT BONUS";
    
    // Отправляем данные обратно в ТГ бот
    tg.sendData(finalPrize); 
    
    // Закрываем WebApp
    tg.close(); 
});

// Первый рендер при загрузке
drawWheel();
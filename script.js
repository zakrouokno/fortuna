const tg = window.Telegram.WebApp;
tg.expand();

const canvas = document.getElementById('wheel');
const ctx = canvas.getContext('2d');
const spinBtn = document.getElementById('spin-btn');
const modal = document.getElementById('win-modal');
const prizeText = document.getElementById('prize-text');
const claimBtn = document.getElementById('claim-btn');

// Сочный список призов для Украины
const prizes = [
    "250 ФС + 200% БОНУС",
    "50 БЕЗКОШТОВНИХ СПІНІВ",
    "150% НА ПЕРШИЙ ДЕПОЗИТ",
    "100 БЕЗКОШТОВНИХ СПІНІВ",
    "VIP ПРОМОКОД НА БЕЗДЕП",
    "30 БЕЗКОШТОВНИХ СПІНІВ"
];

// Премиальная темная палитра
const colors = ["#171926", "#10121a", "#171926", "#10121a", "#171926", "#10121a"];
const numSectors = prizes.length;
const arc = 2 * Math.PI / numSectors;

let currentAngle = 0; // Текущий угол поворота колеса
let isSpinning = false;
let selectedPrize = "";

// Отрисовка колеса на Canvas
function drawWheel() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const radius = canvas.width / 2;
    const center = radius;

    ctx.save();
    ctx.translate(center, center);
    ctx.rotate(currentAngle); // Поворачиваем весь холст на текущий угол анимации
    ctx.translate(-center, -center);

    for (let i = 0; i < numSectors; i++) {
        const angle = i * arc;
        ctx.fillStyle = colors[i];
        
        // Сектор
        ctx.beginPath();
        ctx.moveTo(center, center);
        ctx.arc(center, center, radius - 6, angle, angle + arc);
        ctx.lineTo(center, center);
        ctx.fill();
        
        // Стильные темные разделительные линии
        ctx.strokeStyle = "#1f2230";
        ctx.lineWidth = 2;
        ctx.stroke();

        // Рендер дорогого шрифта текста внутри сектора
        ctx.save();
        ctx.fillStyle = "#8a8f9f";
        
        // Подсвечиваем супер-призы неоновым цианом
        if (prizes[i].includes("250 ФС") || prizes[i].includes("VIP")) {
            ctx.fillStyle = "#00f0ff";
        }
        
        ctx.translate(center, center);
        ctx.rotate(angle + arc / 2);
        ctx.textAlign = "right";
        ctx.font = "bold 11px 'Inter', sans-serif";
        ctx.letterSpacing = "0.5px";
        ctx.fillText(prizes[i], radius - 25, 4);
        ctx.restore();
    }

    // Тонкий неоновый внешний ободок
    ctx.beginPath();
    ctx.arc(center, center, radius - 6, 0, 2 * Math.PI);
    ctx.strokeStyle = "rgba(0, 240, 255, 0.25)";
    ctx.lineWidth = 1.5;
    ctx.stroke();

    ctx.restore();
}

// Запуск кручения
spinBtn.addEventListener('click', () => {
    if (isSpinning) return;
    isSpinning = true;

    // Слегка приглушаем кнопку, показывая, что процесс пошел
    spinBtn.style.opacity = '0.3';
    spinBtn.style.pointerEvents = 'none';

    // ЧЕСТНЫЙ РАНДОМ: Выбираем абсолютно случайный индекс сектора от 0 до 5
    const randomSectorIndex = Math.floor(Math.random() * numSectors);
    selectedPrize = prizes[randomSectorIndex];

    // Высчитываем целевой угол, на котором колесо должно остановиться.
    // Маркер находится ровно вверху (угол -Math.PI / 2).
    const sectorAngle = (2 * Math.PI) / numSectors;
    const targetAngle = (3 * Math.PI / 2) - (randomSectorIndex * sectorAngle) - (sectorAngle / 2);
    
    // Делаем 6 полных оборотов для лютой динамики + выходим на нужный угол
    const totalRotation = (2 * Math.PI * 6) + targetAngle - (currentAngle % (2 * Math.PI));
    
    const startRotation = currentAngle;
    const duration = 5000; // 5 секунд сочного кручения
    const startTimestamp = performance.now();

    function animate(now) {
        const elapsed = now - startTimestamp;
        const progress = Math.min(elapsed / duration, 1);
        
        // Плавное кубическое замедление (Ease-out)
        const easeOut = 1 - Math.pow(1 - progress, 4);
        
        currentAngle = startRotation + (totalRotation * easeOut);
        
        drawWheel();

        if (progress < 1) {
            requestAnimationFrame(animate);
        } else {
            // Колесо остановилось! Выводим именно тот приз, который выпал
            setTimeout(() => {
                prizeText.innerText = selectedPrize.toUpperCase();
                modal.classList.add('show');
            }, 500);
        }
    }

    requestAnimationFrame(animate);
});

// Кнопка забрать бонус
claimBtn.addEventListener('click', () => {
    // Отправляем реально выигранный приз обратно в ТГ бот
    tg.sendData(selectedPrize); 
    tg.close(); 
});

// Отрисовка при старте
document.fonts.ready.then(() => {
    drawWheel();
});

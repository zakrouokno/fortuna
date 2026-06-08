const tg = window.Telegram.WebApp;
tg.expand();

const spinBtn = document.getElementById('spin-btn');
const modal = document.getElementById('win-modal');
const claimBtn = document.getElementById('claim-btn');

let isSpinning = false;
const cards = [
    document.getElementById('card-0'),
    document.getElementById('card-1'),
    document.getElementById('card-2')
];

// Логика "кручения" барабана карт
spinBtn.addEventListener('click', () => {
    if (isSpinning) return;
    isSpinning = true;

    spinBtn.style.opacity = '0.4';
    spinBtn.style.pointerEvents = 'none';

    let currentIndex = 1; 
    let speed = 60; // Начальная бешеная скорость переключения
    let iterations = 0;
    const maxIterations = 35; // Сколько раз карты мигнут перед стопом

    function cycleCards() {
        // Убираем класс active у всех карт
        cards.forEach(c => c.classList.remove('active'));
        
        // Меняем индекс
        currentIndex = (currentIndex + 1) % cards.length;
        cards[currentIndex].classList.add('active');

        iterations++;

        if (iterations < maxIterations) {
            // Постепенно замедляем переключение к концу
            if (iterations > maxIterations - 10) {
                speed += 35;
            }
            setTimeout(cycleCards, speed);
        } else {
            // ХАРДКОД СТОПА: Жестко гасим анимацию на карточке №1 (БЕЗДЕПИ)
            cards.forEach(c => c.classList.remove('active'));
            currentIndex = 1; 
            cards[currentIndex].classList.add('active');

            // Показываем окно победы
            setTimeout(() => {
                modal.classList.add('show');
            }, 600);
        }
    }

    // Запуск цикла
    setTimeout(cycleCards, speed);
});

claimBtn.addEventListener('click', () => {
    const finalPrize = "БЕЗДЕПОЗИТНИЙ БОНУС: 250 ФС + 200% НА ДЕПОЗИТ";
    tg.sendData(finalPrize); 
    tg.close(); 
});

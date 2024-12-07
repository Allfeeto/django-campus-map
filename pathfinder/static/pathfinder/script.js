    <!-- Добавление масштабирования к центру курсора -->


    const container = document.getElementById('map-container');
    const wrapper = document.getElementById('map-wrapper');
    let scale = 0.2; // Установить минимальный масштаб при загрузке
    let translateX = 0, translateY = 0; // Текущая позиция
    let isDragging = false;
    let startX, startY, touchStartX, touchStartY;

    // Получить размеры карты и контейнера
    const mapWidth = 4500; // Ширина карты (в пикселях)
    const mapHeight = 2500; // Высота карты (в пикселях)
    const containerWidth = container.offsetWidth;
    const containerHeight = container.offsetHeight;

    // Применение начального масштаба
// Инициализация трансформации карты
function initializeTransform() {
    const container = document.getElementById('map-container');
    const wrapper = document.getElementById('map-wrapper');
    let scale = 0.2; // Начальный масштаб
    let translateX = 0, translateY = 0; // Позиция
    let isDragging = false;
    let startX, startY, touchStartX, touchStartY;

    // Применение начального масштаба
    wrapper.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;

    // Масштабирование с учётом центра курсора
    container.addEventListener('wheel', (e) => {
        e.preventDefault();
        const scaleAmount = 0.1;
        const oldScale = scale;

        if (e.deltaY < 0) {
            scale += scaleAmount; // Увеличение масштаба
        } else {
            scale = Math.max(0.2, scale - scaleAmount); // Минимальный масштаб
        }

        const rect = container.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        const offsetX = (mouseX - translateX) / oldScale;
        const offsetY = (mouseY - translateY) / oldScale;

        translateX = mouseX - offsetX * scale;
        translateY = mouseY - offsetY * scale;

        wrapper.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
    });

    // Перетаскивание карты
    container.addEventListener('mousedown', (e) => {
        e.preventDefault(); // Отключаем выделение текста
        isDragging = true;
        startX = e.clientX - translateX;
        startY = e.clientY - translateY;
    });

    container.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        translateX = e.clientX - startX;
        translateY = e.clientY - startY;
        wrapper.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
    });

    container.addEventListener('mouseup', () => isDragging = false);
    container.addEventListener('mouseleave', () => isDragging = false);

    // Обработка касаний для мобильных устройств
    container.addEventListener('touchstart', (e) => {
        if (e.touches.length === 1) {
            isDragging = true;
            touchStartX = e.touches[0].clientX - translateX;
            touchStartY = e.touches[0].clientY - translateY;
        }
    });

    container.addEventListener('touchmove', (e) => {
        if (!isDragging || e.touches.length !== 1) return;
        translateX = e.touches[0].clientX - touchStartX;
        translateY = e.touches[0].clientY - touchStartY;
        wrapper.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
    });

    container.addEventListener('touchend', () => isDragging = false);
    container.addEventListener('touchcancel', () => isDragging = false);
}

// Применяем инициализацию карты после загрузки нового SVG
$(document).on('click', '.btn-floor', function(event) {
    event.preventDefault();
    var floor = $(this).data('floor');
    var start_node = $('#id_start').val();
    var end_node = $('#id_end').val();

    var data = { floor: floor };
    if (start_node && end_node) {
        data.start = start_node;
        data.end = end_node;
    }

    $.ajax({
        url: "/map/",
        type: 'GET',
        data: data,
        success: function(response) {
            // Обновляем карту
            $('#map-wrapper').html(response.map_html);

            // Инициализируем трансформацию для нового SVG
            initializeTransform(); // Важно вызывать снова

            // Обновляем форму для построения маршрута
            $('#route-form').html(response.route_form_html);

            // Если маршрут был построен, добавляем его снова
            if (response.path_overlay) {
                $('#map-overlay').html(response.path_overlay);
            }
        },
        error: function(xhr, status, error) {
            console.error("Ошибка при переключении этажа:", status, error);
        }
    });
});


    // Масштабирование с учётом центра курсора
    container.addEventListener('wheel', (e) => {
        e.preventDefault();

        const scaleAmount = 0.1;
        const oldScale = scale;

        // Новое значение масштаба
        if (e.deltaY < 0) {
            scale += scaleAmount; // Увеличение масштаба
        } else {
            scale = Math.max(0.2, scale - scaleAmount); // Минимальный масштаб
        }

        const rect = container.getBoundingClientRect();

        // Координаты курсора относительно контейнера
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        // Вычисление сдвига для центрирования курсора
        const offsetX = (mouseX - translateX) / oldScale;
        const offsetY = (mouseY - translateY) / oldScale;

        translateX = mouseX - offsetX * scale;
        translateY = mouseY - offsetY * scale;

        updateTransform();
    });

    // Ограничить координаты перемещения
    function clampPosition() {
        const scaledWidth = mapWidth * scale;
        const scaledHeight = mapHeight * scale;

        // Лимиты по горизонтали
        const minX = Math.min(0, containerWidth - scaledWidth);
        const maxX = 0;

        // Лимиты по вертикали
        const minY = Math.min(0, containerHeight - scaledHeight);
        const maxY = 0;

        translateX = Math.max(minX, Math.min(maxX, translateX));
        translateY = Math.max(minY, Math.min(maxY, translateY));
    }

    // Начало перемещения карты (мышь)
    container.addEventListener('mousedown', (e) => {
        e.preventDefault(); // Отключаем выделение текста
        isDragging = true;
        startX = e.clientX - translateX;
        startY = e.clientY - translateY;
    });

    // Перемещение карты (мышь)
    container.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        translateX = e.clientX - startX;
        translateY = e.clientY - startY;
        clampPosition(); // Применить ограничения
        updateTransform();
    });

    // Завершение перемещения карты (мышь)
    container.addEventListener('mouseup', () => isDragging = false);
    container.addEventListener('mouseleave', () => isDragging = false);

    // Обработка касаний (тачскрин)
    container.addEventListener('touchstart', (e) => {
        if (e.touches.length === 1) {
            // Одно касание — перемещение
            isDragging = true;
            touchStartX = e.touches[0].clientX - translateX;
            touchStartY = e.touches[0].clientY - translateY;
        }
    });


    let initialDistance = null;
    let initialCenter = null;

    // Рассчитать центр между двумя пальцами
    function getTouchCenter(touches) {
        const x = (touches[0].clientX + touches[1].clientX) / 2;
        const y = (touches[0].clientY + touches[1].clientY) / 2;
        return { x, y };
    }

    // Начало масштабирования
    container.addEventListener('touchstart', (e) => {
        if (e.touches.length === 2) {
            const dx = e.touches[0].clientX - e.touches[1].clientX;
            const dy = e.touches[0].clientY - e.touches[1].clientY;
            initialDistance = Math.sqrt(dx * dx + dy * dy);
            initialCenter = getTouchCenter(e.touches); // Сохраняем начальный центр
        }
    });

    // Масштабирование
    container.addEventListener('touchmove', (e) => {
        if (e.touches.length === 2 && initialDistance) {
            e.preventDefault();

            const dx = e.touches[0].clientX - e.touches[1].clientX;
            const dy = e.touches[0].clientY - e.touches[1].clientY;
            const currentDistance = Math.sqrt(dx * dx + dy * dy);

            // Новый масштаб
            const scaleChange = currentDistance / initialDistance;
            const newScale = Math.max(0.2, scale * scaleChange); // Минимальный масштаб

            // Центр между пальцами
            const currentCenter = getTouchCenter(e.touches);

            // Смещение карты
            const rect = container.getBoundingClientRect();
            const offsetX = (currentCenter.x - rect.left - translateX) / scale;
            const offsetY = (currentCenter.y - rect.top - translateY) / scale;

            // Пересчёт положения для сохранения центра
            translateX = currentCenter.x - rect.left - offsetX * newScale;
            translateY = currentCenter.y - rect.top - offsetY * newScale;

            scale = newScale;
            initialDistance = currentDistance; // Обновляем расстояние
            updateTransform();
        }
    });

    // Завершение масштабирования
    container.addEventListener('touchend', () => {
        if (initialDistance) {
            initialDistance = null;
            initialCenter = null;
        }
    });





    container.addEventListener('touchmove', (e) => {
        if (!isDragging || e.touches.length !== 1) return;
        translateX = e.touches[0].clientX - touchStartX;
        translateY = e.touches[0].clientY - touchStartY;
        clampPosition(); // Применить ограничения
        updateTransform();
    });

    container.addEventListener('touchend', () => isDragging = false);
    container.addEventListener('touchcancel', () => isDragging = false);

    // Обновление трансформации
    function updateTransform() {
        wrapper.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
    }



    // Функция для центрирования изображения в контейнере
    function centerMap() {
        // Получаем размеры контейнера
        const containerWidth = container.offsetWidth;
        const containerHeight = container.offsetHeight;

        // Рассчитываем смещение для центрирования карты (с учётом масштаба)
        translateX = (containerWidth - mapWidth * scale) / 2;
        translateY = (containerHeight - mapHeight * scale) / 2;

        // Применяем трансформацию (сдвиг и масштаб)
        updateTransform();
    }

    // Обновление трансформации
    function updateTransform() {
        wrapper.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
    }

    // Инициализация при загрузке страницы
    window.addEventListener('load', centerMap);
    window.addEventListener('resize', centerMap); // Центрируем карту при изменении размера окна





    // Инициализация карты
    initializeTransform();
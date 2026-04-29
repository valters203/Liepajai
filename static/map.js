document.addEventListener('DOMContentLoaded', function() {
    const mapContainer = document.getElementById('map-container');
    const mapWrapper = document.getElementById('map-wrapper');
    const map = document.getElementById('map');
    const tooltip = document.getElementById('tooltip');
    let x = 0;
    let y = 0;
    let scale = 1;
    const speed = 7;
    const zoomSpeed = 0.1;
    const minScale = 0.5;
    const maxScale = 2;
    let isDragging = false;
    let startX = 0;
    let startY = 0;
    let dragStartX = 0;
    let dragStartY = 0;
    let clickSuppressed = false;

    function clampPosition() {
        const minX = Math.min(0, mapContainer.clientWidth - map.clientWidth * scale);
        const minY = Math.min(0, mapContainer.clientHeight - map.clientHeight * scale);
        if (x > 0) x = 0;
        if (x < minX) x = minX;
        if (y > 0) y = 0;
        if (y < minY) y = minY;
    }

    function fitMapInView() {
        if (map.naturalWidth === 0 || map.naturalHeight === 0) return;
        
        const containerWidth = mapContainer.clientWidth;
        const containerHeight = mapContainer.clientHeight;
        const mapWidth = map.naturalWidth;
        const mapHeight = map.naturalHeight;
        
        // Calculate scale to fit entire map in container
        scale = Math.min(containerWidth / mapWidth, containerHeight / mapHeight, maxScale);
        
        // Center the map
        const scaledWidth = mapWidth * scale;
        const scaledHeight = mapHeight * scale;
        x = (containerWidth - scaledWidth) / 2;
        y = (containerHeight - scaledHeight) / 2;
        
        clampPosition();
        updateTransform();
    }

    function updateTransform() {
        clampPosition();
        mapWrapper.style.transform = `translate(${x}px, ${y}px) scale(${scale})`;
    }

    // Tooltip functionality
    const mapButtons = document.querySelectorAll('.map-btn');
    mapButtons.forEach(btn => {
        btn.addEventListener('mouseenter', function(e) {
            const name = btn.dataset.name;
            tooltip.textContent = name;
            tooltip.style.display = 'block';
            updateTooltipPosition(e);
        });
        
        btn.addEventListener('mousemove', updateTooltipPosition);
        
        btn.addEventListener('mouseleave', function() {
            tooltip.style.display = 'none';
        });
    });

    function updateTooltipPosition(e) {
        tooltip.style.left = (e.clientX + 10) + 'px';
        tooltip.style.top = (e.clientY + 10) + 'px';
    }

    document.addEventListener('keydown', function(event) {
        switch(event.key) {
            case 'ArrowLeft':
                x += speed;
                break;
            case 'ArrowRight':
                x -= speed;
                break;
            case 'ArrowUp':
                y += speed;
                break;
            case 'ArrowDown':
                y -= speed;
                break;
        }
        updateTransform();
    });

    document.addEventListener('wheel', function(event) {
        event.preventDefault();
        if (event.deltaY < 0) {
            scale += zoomSpeed;
        } else {
            scale -= zoomSpeed;
        }
        if (scale < minScale) scale = minScale;
        if (scale > maxScale) scale = maxScale;
        updateTransform();
    });

    mapWrapper.addEventListener('mousedown', function(event) {
        if (event.button !== 0) return;
        if (event.target.closest('.map-btn')) return;
        isDragging = true;
        startX = event.clientX;
        startY = event.clientY;
        dragStartX = x;
        dragStartY = y;
        mapContainer.classList.add('dragging');
        clickSuppressed = false;
        event.preventDefault();
    });

    document.addEventListener('mousemove', function(event) {
        if (!isDragging) return;
        const dx = event.clientX - startX;
        const dy = event.clientY - startY;
        x = dragStartX + dx;
        y = dragStartY + dy;
        updateTransform();
        if (Math.abs(dx) + Math.abs(dy) > 5) {
            clickSuppressed = true;
        }
    });

    document.addEventListener('mouseup', function(event) {
        if (!isDragging) return;
        isDragging = false;
        mapContainer.classList.remove('dragging');
        setTimeout(() => { clickSuppressed = false; }, 50);
    });

    mapButtons.forEach(btn => {
        btn.addEventListener('click', function(event) {
            if (clickSuppressed) {
                event.preventDefault();
            }
        });
    });

    // Fit map in view when image loads
    if (map.complete) {
        // Image is already cached
        fitMapInView();
    } else {
        // Wait for image to load
        map.addEventListener('load', fitMapInView);
    }

    updateTransform();
});
/* Slider 工具函數 - FRAND 費率評估 */

/** 創建 slider */
function createSlider(inputName, displayId, min = 0, max = 20, step = 0.1, prefix = '$') {
    const numberInput = document.querySelector(`input[name="${inputName}"]`);
    if (!numberInput) return;

    const slider = document.createElement('input');
    slider.type = 'range';
    slider.min = min.toString();
    slider.max = max.toString();
    slider.step = step.toString();
    slider.style.width = '100%';
    slider.style.height = '20px';
    slider.style.cursor = 'pointer';
    
    const display = document.getElementById(displayId);
    
    if (numberInput.value && numberInput.value.trim() !== '') {
        slider.value = numberInput.value;
        if (display) {
            display.textContent = prefix + parseFloat(slider.value).toFixed(1);
        }
    } else {
        slider.value = min.toString();
        if (display) display.textContent = '';
        numberInput.value = '';
    }

    function updateDisplay() {
        const value = parseFloat(slider.value).toFixed(1);
        if (display) {
            display.textContent = prefix + value;
        }
        numberInput.value = value;
    }
    
    slider.addEventListener('input', updateDisplay);
    
    numberInput.style.display = 'none';
    numberInput.parentNode.insertBefore(slider, numberInput.nextSibling);
}

/** 批量創建 sliders */
function initializeSliders(sliderConfigs) {
    function init() {
        sliderConfigs.forEach(config => {
            createSlider(
                config.inputName,
                config.displayId,
                config.min || 0,
                config.max || 20,
                config.step || 0.1,
                config.prefix || '$'
            );
        });
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
}

/** 添加刻度標記 */
function addSliderTicks(containerId, ticks, prefix = '$') {
    const container = document.getElementById(containerId);
    if (!container) return;

    const ticksDiv = document.createElement('div');
    ticksDiv.className = 'slider-ticks';
    
    ticks.forEach(tick => {
        const span = document.createElement('span');
        span.textContent = prefix + tick;
        ticksDiv.appendChild(span);
    });
    
    container.appendChild(ticksDiv);
}

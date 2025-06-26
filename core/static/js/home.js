// Archivo: core/static/js/home.js
document.addEventListener('DOMContentLoaded', async function() {
    try {
        // Obtener datos de productividad desde la API
        const response = await fetch('/planner/api/productividad/');
        const data = await response.json();
        console.log('📊 Datos de productividad cargados:', data);
        
        // Crear array con 7 ceros
        const productividadData = [0, 0, 0, 0, 0, 0, 0];
        
        // Si hay datos y día, colocar el porcentaje en el día correcto
        if (data.productividad !== undefined && data.dia !== undefined) {
            productividadData[data.dia] = data.productividad;
            console.log('📊 Día de actividad:', data.dia);
            console.log('📊 Porcentaje:', data.productividad);
        }

        // Convertir a formato esperado por el gráfico
        const dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
        const productivityData = dias.map((name, index) => ({
            name,
            percentage: productividadData[index]
        }));
        
        // Crear el gráfico de barras mejorado con D3.js
        createBarChart(productivityData);
        
        // Actualizar el porcentaje en el indicador
        const productivityIndicator = document.querySelector('[data-productivity-indicator]');
        if (productivityIndicator) {
            productivityIndicator.textContent = `${data.productividad || 0}%`;
        }
        
    } catch (error) {
        console.error('❌ Error al obtener datos de productividad:', error);
    }
});

function createBarChart(productivityData) {
    // Configuración de colores
    const colors = ['#6EE7B7', '#3B82F6', '#818CF8', '#A78BFA', '#F472B6', '#FBBF24', '#F87171'];
    const dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];

    // Dimensiones y márgenes
    const container = document.getElementById('dashboardBarChart');
    if (!container) {
        console.warn('⚠️ No se encontró el contenedor del gráfico');
        return;
    }

    const margin = {
        top: 40,      // Aumentado para el título
        right: 30,    // Ajustado para mejor espaciado
        bottom: 40,   // Reducido para aprovechar espacio
        left: 60      // Aumentado para etiquetas del eje Y
    };
    
    // Calcular dimensiones reales del área de dibujo
    const width = container.offsetWidth - margin.left - margin.right;
    const height = container.offsetHeight - margin.top - margin.bottom;

    // Crear el elemento SVG con dimensiones precisas
    const svg = d3.select("#dashboardBarChart")
        .append("svg")
        .style("width", "100%")
        .style("height", "100%")
        .style("display", "block")
        .attr("preserveAspectRatio", "xMidYMid meet")
        .attr("viewBox", `0 0 ${container.offsetWidth} ${container.offsetHeight}`)
        .style("background", "transparent");

    // Grupo principal con transformación ajustada
    const g = svg.append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Escalas
    const x = d3.scaleBand()
        .range([0, width])
        .domain(dias)
        .padding(0.2);

    const y = d3.scaleLinear()
        .range([height, 0])
        .domain([0, 100]);

    // Gradientes para las barras
    const defs = svg.append("defs");
    
    colors.forEach((color, i) => {
        const gradient = defs.append("linearGradient")
            .attr("id", `gradient-dashboard-${i}`)
            .attr("gradientUnits", "userSpaceOnUse")
            .attr("x1", 0).attr("y1", height)
            .attr("x2", 0).attr("y2", 0);
        
        gradient.append("stop")
            .attr("offset", "0%")
            .attr("stop-color", color)
            .attr("stop-opacity", 0.8);
        
        gradient.append("stop")
            .attr("offset", "100%")
            .attr("stop-color", d3.color(color).brighter(0.5))
            .attr("stop-opacity", 1);
    });

    // Líneas de cuadrícula horizontales
    g.append("g")
        .attr("class", "grid")
        .selectAll("line")
        .data(y.ticks(5))
        .enter()
        .append("line")
        .attr("x1", 0)
        .attr("x2", width)
        .attr("y1", d => y(d))
        .attr("y2", d => y(d))
        .attr("stroke", "#374151")
        .attr("stroke-width", 0.5)
        .attr("stroke-dasharray", "3,3")
        .attr("opacity", 0.3);

    // Eje X mejorado
    g.append("g")
        .attr("class", "x-axis")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x).tickSize(0))
        .selectAll("text")
        .style("fill", "#D1D5DB")
        .style("font-family", "'Inter', sans-serif")
        .style("font-size", "12px")
        .style("font-weight", "500");

    // Eje Y mejorado
    g.append("g")
        .attr("class", "y-axis")
        .call(d3.axisLeft(y)
            .ticks(5)
            .tickSize(0)
            .tickFormat(d => d + "%"))
        .selectAll("text")
        .style("fill", "#D1D5DB")
        .style("font-family", "'Inter', sans-serif")
        .style("font-size", "12px")
        .style("font-weight", "500");

    // Remover líneas de los ejes
    g.selectAll(".domain").remove();

    // Crear barras con efectos mejorados
    const data = productivityData.map(item => item.percentage);
    const bars = g.selectAll(".bar")
        .data(data)
        .enter()
        .append("rect")
        .attr("class", "bar")
        .attr("x", (d, i) => x(dias[i]))
        .attr("width", x.bandwidth())
        .attr("y", height)
        .attr("height", 0)
        .attr("fill", (d, i) => `url(#gradient-dashboard-${i})`)
        .attr("rx", 8)
        .attr("ry", 8)
        .style("filter", "drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1))")
        .style("cursor", "pointer");

    // Animación de entrada
    bars.transition()
        .duration(1200)
        .delay((d, i) => i * 100)
        .ease(d3.easeBounceOut)
        .attr("y", d => y(d))
        .attr("height", d => height - y(d));

    // Agregar valores en la parte superior de las barras
    const labels = g.selectAll(".bar-label")
        .data(data)
        .enter()
        .append("text")
        .attr("class", "bar-label")
        .attr("x", (d, i) => x(dias[i]) + x.bandwidth() / 2)
        .attr("y", height)
        .attr("text-anchor", "middle")
        .style("fill", "#A855F7")
        .style("font-family", "'Inter', sans-serif")
        .style("font-size", "14px")
        .style("font-weight", "600")
        .style("opacity", 0)
        .text(d => d > 0 ? d + "%" : "");

    // Animación de las etiquetas
    labels.transition()
        .duration(1200)
        .delay((d, i) => i * 100 + 600)
        .attr("y", d => d > 0 ? y(d) - 10 : height)
        .style("opacity", d => d > 0 ? 1 : 0);

    // Tooltip mejorado
    const tooltip = d3.select("body")
        .append("div")
        .attr("class", "fixed z-50 bg-gray-900 text-white px-4 py-3 rounded-xl text-sm pointer-events-none opacity-0 transition-all duration-300 shadow-2xl border border-gray-700")
        .style("backdrop-filter", "blur(10px)");

    // Interactividad mejorada
    bars.on("mouseover", function(event, d) {
            const i = data.indexOf(d);
            
            // Efecto de resaltado con escala y brillo
            d3.select(this)
                .transition()
                .duration(200)
                .attr("transform", "scale(1.05)")
                .style("filter", "drop-shadow(0 8px 16px rgba(168, 85, 247, 0.4)) brightness(1.1)");
            
            // Mostrar tooltip con animación
            tooltip.transition()
                .duration(200)
                .style("opacity", 1);
            
            tooltip.html(`
                <div class="flex items-center gap-2 mb-1">
                    <div class="w-3 h-3 rounded-full" style="background-color: ${colors[i]}"></div>
                    <span class="font-semibold text-white">${dias[i]}</span>
                </div>
                <div class="text-purple-300 text-xs">Productividad: <span class="font-bold">${d}%</span></div>
                ${d > 0 ? `<div class="text-gray-400 text-xs mt-1">¡Buen trabajo! 🎉</div>` : `<div class="text-gray-400 text-xs mt-1">Día libre 😴</div>`}
            `)
                .style("left", (event.pageX + 15) + "px")
                .style("top", (event.pageY - 10) + "px");
        })
        .on("mouseout", function(event, d) {
            // Restaurar estado original
            d3.select(this)
                .transition()
                .duration(200)
                .attr("transform", "scale(1)")
                .style("filter", "drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1))");
            
            tooltip.transition()
                .duration(300)
                .style("opacity", 0);
        });
}

// Manejar redimensionamiento de ventana con debounce
let resizeTimeout;
window.addEventListener('resize', function() {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(function() {
        // Limpiar gráfico existente
        d3.select("#dashboardBarChart").selectAll("*").remove();
        
        // Recrear gráfico
        const productivityDataElement = document.getElementById('productivity-data');
        if (productivityDataElement) {
            try {
                const productivityData = JSON.parse(productivityDataElement.textContent.trim());
                createBarChart(productivityData);
            } catch (error) {
                console.error('❌ Error al procesar datos de productividad:', error);
            }
        }
    }, 250);
});

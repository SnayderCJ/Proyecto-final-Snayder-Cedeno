// Archivo: static/js/productividad.js
document.addEventListener("DOMContentLoaded", async function () {
    // Función para obtener datos de productividad desde la API
    async function obtenerDatosProductividad() {
        try {
            const response = await fetch('/planner/api/productividad/');
            const data = await response.json();
            // Usar los datos de productividad de toda la semana
            const productividadData = data.productividad_dias || [0, 0, 0, 0, 0, 0, 0];
            console.log('📊 Datos de productividad:', productividadData);
            
            // Calcular el porcentaje del día actual
            const diaActual = data.dia_actual;
            const porcentajeHoy = productividadData[diaActual] || 0;
            
            return {
                productividadData: productividadData,
                porcentaje: porcentajeHoy
            };
        } catch (error) {
            console.error('Error al obtener datos de productividad:', error);
            return {
                productividadData: [0, 0, 0, 0, 0, 0, 0],
                porcentaje: 0
            };
        }
    }

    // Siempre obtener datos de la API para asegurar consistencia
    const datos = await obtenerDatosProductividad();
    let productividadData = datos.productividadData;
    let porcentaje = datos.porcentaje;
    
    // Actualizar elementos del DOM con los nuevos datos
    const porcentajeElements = document.querySelectorAll('[data-productivity-value]');
    porcentajeElements.forEach(el => {
        el.textContent = `${porcentaje}%`;
    });
    
    // Configuración de colores
    const colors = ['#6EE7B7', '#3B82F6', '#818CF8', '#A78BFA', '#F472B6', '#FBBF24', '#F87171'];
    const dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];

    // Crear gráficos
    createBarChart();
    const donutContainer = document.getElementById('donutChart');
    if (donutContainer) {
        createDonutChart();
    }

    function createBarChart() {
        // Dimensiones y márgenes ajustados para ocupar todo el espacio
        const container = document.getElementById('barChart') || document.getElementById('dashboardBarChart');
        if (!container) {
            console.warn('⚠️ No se encontró el contenedor del gráfico de barras');
            return;
        }
        const margin = {
            top: 60,      // Aumentado más para el título y valores altos
            right: 30,    // Ajustado para mejor espaciado
            bottom: 40,   // Reducido para aprovechar espacio
            left: 60      // Aumentado para etiquetas del eje Y
        };
        
        // Calcular dimensiones reales del área de dibujo
        const width = container.offsetWidth - margin.left - margin.right;
        const height = container.offsetHeight - margin.top - margin.bottom;

        // Crear el elemento SVG con dimensiones precisas
        const containerId = container.id;
        const svg = d3.select(`#${containerId}`)
            .append("svg")
            .style("width", "100%")
            .style("height", "100%")
            .style("display", "block") // Evita espacio extra debajo del SVG
            .attr("preserveAspectRatio", "xMidYMid meet")
            .attr("viewBox", `0 0 ${container.offsetWidth} ${container.offsetHeight}`)
            .style("background", "transparent");

        // Grupo principal con transformación ajustada
        const g = svg.append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        // Escalas mejoradas
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
                .attr("id", `gradient-${i}`)
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
        const bars = g.selectAll(".bar")
            .data(productividadData)
            .enter()
            .append("rect")
            .attr("class", "bar")
            .attr("x", (d, i) => x(dias[i]))
            .attr("width", x.bandwidth())
            .attr("y", height)
            .attr("height", 0)
            .attr("fill", (d, i) => `url(#gradient-${i})`)
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
            .data(productividadData)
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
            .attr("y", d => d > 0 ? y(d) - 20 : height) // Aumentado el espacio para los valores
            .style("opacity", d => d > 0 ? 1 : 0);

        // Tooltip mejorado
        const tooltip = d3.select("body")
            .append("div")
            .attr("class", "fixed z-50 bg-gray-900 text-white px-4 py-3 rounded-xl text-sm pointer-events-none opacity-0 transition-all duration-300 shadow-2xl border border-gray-700")
            .style("backdrop-filter", "blur(10px)");

        // Interactividad mejorada
        bars.on("mouseover", function(event, d) {
                const i = productividadData.indexOf(d);
                const rect = this.getBoundingClientRect();
                
                // Efecto de resaltado con escala y brillo
                d3.select(this)
                    .transition()
                    .duration(200)
                    .style("filter", "drop-shadow(0 8px 16px rgba(168, 85, 247, 0.4)) brightness(1.1)");
                
                // Mostrar tooltip con animación, posicionado arriba de la barra
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
                    .style("left", `${rect.left + (rect.width / 2)}px`)
                    .style("top", `${rect.top - 80}px`); // Posicionar arriba de la barra
            })
            .on("mouseout", function(event, d) {
                // Restaurar estado original
                d3.select(this)
                    .transition()
                    .duration(200)
                    .style("filter", "drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1))");
                
                tooltip.transition()
                    .duration(300)
                    .style("opacity", 0);
            });

        // Agregar título del gráfico
        g.append("text")
            .attr("x", width / 2)
            .attr("y", -30) // Mover el título más arriba
            .attr("text-anchor", "middle")
            .style("fill", "#D1D5DB")
            .style("font-family", "'Inter', sans-serif")
            .style("font-size", "16px")
            .style("font-weight", "600")
            .text("Productividad Semanal");
    }

    function createDonutChart() {
        // Dimensiones basadas en el contenedor
        const container = document.getElementById('donutChart');
        if (!container) {
            console.warn('⚠️ No se encontró el contenedor del gráfico donut');
            return;
        }
        const width = container.offsetWidth;
        const height = container.offsetHeight;
        const radius = Math.min(width, height) * 0.4; // Reducir el radio para que quepa mejor

        // Crear el elemento SVG
        const svg = d3.select("#donutChart")
            .append("svg")
            .attr("width", width)
            .attr("height", height)
            .append("g")
            .attr("transform", `translate(${width/2},${height/2})`);

        // Obtener el porcentaje del día actual (día con actividad)
        const hoy = new Date().getDay(); // 0=Domingo, 1=Lunes, etc.
        const diaActual = hoy === 0 ? 6 : hoy - 1; // Convertir a formato 0=Lunes
        
        // Buscar el día con actividad en los datos
        let porcentajeDiaActual = 0;
        for (let i = 0; i < productividadData.length; i++) {
            if (productividadData[i] > 0) {
                porcentajeDiaActual = productividadData[i];
                break; // Usar el primer día con actividad
            }
        }
        
        // Si no hay actividad, usar el porcentaje general
        if (porcentajeDiaActual === 0) {
            porcentajeDiaActual = porcentaje;
        }

        // Datos para el donut usando el porcentaje del día actual
        const data = [
            {name: "Productivo", value: porcentajeDiaActual},
            {name: "Restante", value: 100 - porcentajeDiaActual}
        ];

        // Generador de arco con bordes redondeados
        const arc = d3.arc()
            .innerRadius(radius * 0.75)
            .outerRadius(radius)
            .cornerRadius(8);

        // Generador de pie con espaciado
        const pie = d3.pie()
            .value(d => d.value)
            .sort(null)
            .padAngle(0.02);

        // Colores
        const color = d3.scaleOrdinal()
            .domain(data.map(d => d.name))
            .range(["#A259FF", "#3f3f46"]);

        // Crear grupos para cada segmento
        const arcs = svg.selectAll("arc")
            .data(pie(data))
            .enter()
            .append("g");

        // Agregar paths con animación e interactividad
        const paths = arcs.append("path")
            .attr("d", arc)
            .attr("fill", d => color(d.data.name))
            .style("cursor", "pointer")
            .transition()
            .duration(1200) // Sincronizar con la animación de las barras
            .delay((d, i) => i * 100) // Agregar delay similar a las barras
            .attrTween("d", function(d) {
                const interpolate = d3.interpolate({startAngle: 0, endAngle: 0}, d);
                return function(t) {
                    return arc(interpolate(t));
                };
            });

        // Agregar interactividad a los segmentos
        arcs.selectAll("path")
            .on("mouseover", function(event, d) {
                const segment = d3.select(this);
                const centroid = arc.centroid(d);
                const [x, y] = centroid;
                
                segment
                    .transition()
                    .duration(200)
                    .attr("filter", "brightness(1.2)");

                // Actualizar el texto del centro con el valor específico
                d3.select("#donutPorcentaje")
                    .html(`${Math.round(d.value)}%<br><span class="text-sm font-normal">${d.data.name}</span>`);
            })
            .on("mouseout", function(event, d) {
                d3.select(this)
                    .transition()
                    .duration(200)
                    .attr("filter", null);

                // Restaurar el texto original
                d3.select("#donutPorcentaje")
                    .html(`${porcentajeDiaActual}%`);
            });

        // Actualizar el porcentaje en el centro con animación
        let currentPercentage = 0;
        const duration = 1000;
        const finalPercentage = porcentajeDiaActual;

        d3.select("#donutPorcentaje")
            .transition()
            .duration(duration)
            .tween("text", function() {
                const interpolate = d3.interpolateNumber(currentPercentage, finalPercentage);
                return function(t) {
                    this.textContent = Math.round(interpolate(t)) + "%";
                };
            });
    }

    // Manejar redimensionamiento de ventana con debounce
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function() {
            // Limpiar gráficos existentes
            const barContainer = document.getElementById('barChart') || document.getElementById('dashboardBarChart');
            const donutContainer = document.getElementById('donutChart');
            
            if (barContainer) {
                d3.select(`#${barContainer.id}`).selectAll("*").remove();
            }
            if (donutContainer) {
                d3.select("#donutChart").selectAll("*").remove();
            }
            
            // Recrear gráficos
            createBarChart();
            if (donutContainer) {
                createDonutChart();
            }
        }, 250);
    });
});

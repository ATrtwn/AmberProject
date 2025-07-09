
// Fetch baseline probabilities with no tests selected
function fetchBaseline() {
    fetch('/diagnosis', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({selected_tests: []})
    })
    .then(res => res.json())
    .then(data => {
        baselineProbs = data.probabilities;
        const zeros = new Array(baselineProbs.length).fill(0);
        plotDiagnosis(data.diagnoses, zeros, baselineProbs, data.thresholds);
        document.getElementById("decision").innerHTML = `<div class="recommendation">Please give me symptoms to see changes.</div>`;
    });
}

// Update diagnosis based on selected tests
function updateDiagnosisWithTests(selectedTests) {
    fetch('/diagnosis', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ selected_tests: selectedTests })
    })
    .then(res => res.json())
    .then(data => {
        const deltas = data.probabilities.map((p, i) => p - baselineProbs[i]);
        plotDiagnosis(data.diagnoses, deltas, baselineProbs, data.thresholds);

        // same logic you already have for showing decision text
        const passedDiagnoses = data.diagnoses
          .map((diag, i) => {
            const prob = data.probabilities[i];
            const threshArray = data.thresholds[i];
            const passed = threshArray.filter(t => prob >= t.value);
            return { diag, prob, passed };
          })
          .filter(d => d.passed.length > 0);

        if (passedDiagnoses.length > 0) {
            const lines = passedDiagnoses.map(d => {
                const passedStr = d.passed.map(t => `${t.name}`).join(', ');
                return `<div class="recommendation">
                        • Recommended next steps for ${d.diag} (P = ${d.prob.toFixed(2)}):
                        <br>&nbsp;&nbsp;${passedStr}</div>`;
            });
            document.getElementById("decision").innerHTML = `<div class="recommendation">${lines.join('\n')}</div>`;
        } else {
            const allDeltasZero = deltas.every(delta => delta === 0);

            if (allDeltasZero) {
                document.getElementById("decision").innerHTML = `<div class="recommendation">Still...please give me some symptoms.</div>`;
            } else {
                const maxIndex = data.probabilities.indexOf(Math.max(...data.probabilities));
                const threshArray = data.thresholds[maxIndex];
                const closestThreshObj = threshArray.reduce((min, t) => t.value < min.value ? t : min, threshArray[0]);

                document.getElementById("decision").innerHTML =
                    `<div class="recommendation">No diagnosis exceeds any threshold.<br>` +
                    `Most probable next step: ${closestThreshObj.name || closestThreshObj.class}</div>`;
            }
        }
    });
}

// Plot function with base = baseline probabilities
function plotDiagnosis(diagnoses, deltas, baseline, thresholds) {
    const xTicks = diagnoses.map((_, i) => i);
    // Original colors for baseline bars
    //const baselineColors = new Array(baseline.length).fill('#D3D3D3');

    // Compute the difference (delta) by subtracting the baseline from the total values (y = baseline + delta)
    const deltasForHover = deltas.map((delta, index) => ({
        difference: delta.toFixed(2),  // Format the difference
        sum: (baseline[index] + delta).toFixed(2),  // Calculate the sum (baseline + delta)
        baseline: baseline[index].toFixed(2)  // Include baseline value in hover data
    }));
    const deltaTrace = {
        type: 'bar',
        y: deltas,
        base: baseline,
        marker: {
            color: deltas.map(d => d >= 0 ? '#9fd1c0' : '#f3752d')
        },
        name: 'Delta',
        customdata: deltasForHover,
        hovertemplate: 'Difference: %{customdata.difference}<br>' +
               'Sum: %{customdata.sum}<br>' +
               'Baseline: %{customdata.baseline}<extra></extra>',
        showlegend: false
    };

    // Dummy traces for the legend (positive and negative deltas)
    const positiveDeltaTrace = {
        type: 'scatter',
        mode: 'markers',
        x: [null],  // Just a dummy point
        y: [null],
        marker: {
            color: '#9fd1c0', // Positive delta color (green)
            symbol: 'circle'
        },
        name: 'Positive Delta',
        showlegend: true
    };

    const negativeDeltaTrace = {
        type: 'scatter',
        mode: 'markers',
        x: [null],  // Just a dummy point
        y: [null],
        marker: {
            color: '#f3752d', // Negative delta color (orange)
            symbol: 'circle'
        },
        name: 'Negative Delta',
        showlegend: true
    };

    const baselineLineTrace = {
        type: 'scatter',
        mode: 'lines',
        x: [],
        y: [],
        line: {
            color: '#D3D3D3',  // Line color (light gray)
            width: 2,           // Line width
            dash: 'solid'       // Solid line style
        },
        name: 'Baseline',
        hovertemplate: 'Baseline: %{y:.2f}<extra></extra>',
        hoverinfo: 'y',
        showlegend: false
    };


    // Adjust x and y for baseline line trace (to make it segmented with intermediate points)
    const numPoints = 20; // You can adjust this number for smoother or rougher lines
    diagnoses.forEach((diagnosis, i) => {
        const baselineValue = baseline[i];

        // Adjust x to cover the width of the bars (bars are centered, so we adjust by half the bar width)
        const barWidth = 0.4;
        const xStart = i - barWidth;
        const xEnd = i + barWidth;

        // Add intermediate points between xStart and xEnd
        for (let j = 0; j <= numPoints; j++) {
            const xVal = xStart + (j / numPoints) * (xEnd - xStart); // Smoothly interpolate x values between xStart and xEnd
            baselineLineTrace.x.push(xVal);
            baselineLineTrace.y.push(baselineValue); // Same y value for all points to create a horizontal line
        }

        // Add a small gap between the segments
        if (i < diagnoses.length - 1) {
            baselineLineTrace.x.push(null);
            baselineLineTrace.y.push(null);
        }
    });

    const barWidth = 0.4;
    const shapes = [];

    const thresholdColors = {
      classA: '#ca5708',
      classB: '#dba183'
    };

    const thresholdTraces = [];

    diagnoses.forEach((diagnosis, i) => {
        const threshArray = thresholds[i];
        threshArray.forEach(threshObj => {
            const { value, class: cls, name } = threshObj;
            shapes.push({
              type: 'line',
              xref: 'x',
              yref: 'y',
              x0: i - barWidth,
              x1: i + barWidth,
              y0: value,
              y1: value,
              line: {
                color: thresholdColors[cls] || 'black',  // fallback to black if class unknown
                width: 2,
                dash: 'dot'
              },
            });

            const numPoints = 20;
            const xPoints = [];
            const yPoints = [];
            for (let j = 0; j <= numPoints; j++) {
                const xVal = i - barWidth + (j / numPoints) * (2 * barWidth);
                xPoints.push(xVal);
                yPoints.push(value);
            }

            thresholdTraces.push({
                type: 'scatter',
                mode: 'lines',
                x: xPoints,
                y: yPoints,
                line: {
                    width: 2,
                    color: 'rgba(0,0,0,0)'
                },
                hovertext: name || cls,
                hoverinfo: 'text',
                showlegend: false
            });
        });
    });

    Plotly.newPlot('plot', [
        ...thresholdTraces,
        baselineLineTrace,
        deltaTrace,
        positiveDeltaTrace,
        negativeDeltaTrace
        ], {
         yaxis: {
            title: {
                text: 'Probability',
                font: {
                    family: 'Courier New',
                    size: 15,
                    color: 'black',
                }
            },
             tickfont: {
                family: 'Courier New',
                size: 14,
                color: 'black'
            },
            range: [0, 1.1],
            gridcolor: 'rgba(0, 0, 0, 0.1)',
            gridwidth: 1,
            zeroline: true,
            zerolinecolor: 'lightgrey',
            zerolinewidth: 2
        },
        xaxis: {
            type: 'linear',
            tickmode: 'array',
            tickvals: xTicks,
            ticktext: diagnoses,
            tickfont: {
                family: 'Courier New',
                size: 14,
                color: 'black'
            },
            range: [-0.5, diagnoses.length - 0.5],
            showspikes: false
        },
        hovermode: 'closest',
        hoverdistance: 10,
        hoverlabel: {
            bgcolor: 'rgba(255, 255, 255, 0.9)',
            bordercolor: 'lightgrey',
            font: {
                family: 'Courier New',
                size: 14,
                color: 'black',
                weight: 'bold'
            },
            align: 'center'
        },
        margin: { t: 20 },
        barmode: 'stack',
        shapes: shapes,
        align: 'center',
        padding: 15,
        responsive: true,
        dragmode: false
    }, {
        displayModeBar: false,
        displaylogo: false
    });

    // Add resize event listener to handle window resizing
    window.addEventListener('resize', function() {
        Plotly.Plots.resize(document.getElementById('plot'));
    });
}

// extract input from text area
// call updateDiagnosis with the keywords found by backend
function extractAndSelectSymptoms() {
    const input = document.getElementById("symptom-input").value;
    const text = input.trim();

    const spinner = document.getElementById("loading-spinner");
    const keywordList = document.getElementById("modal-keyword-list");
    const matchedSection = document.getElementById("keywords-modal");
    const showBtn = document.getElementById("show-keywords-btn");

     // If input is empty, skip everything
    if (!text) {
        // Clear the textarea
        document.getElementById("symptom-input").value = "";

        // Hide spinner if visible
        spinner.classList.remove("active");

        // Clear keyword list and reset matched section
        keywordList.innerHTML = "";

        // Show "No keywords found" message
        const li = document.createElement("li");
        li.classList.add("no-keywords");
        keywordList.appendChild(li);
        showBtn.style.display = "none";

        updateDiagnosisWithTests([]);
        return; // Exit early
    }

    // Show spinner, hide previous content
    spinner.classList.add("active");
    matchedSection.style.display = "none";
    keywordList.innerHTML = "";

    fetch('/extract_keywords', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
    })
    .then(res => res.json())
    .then(data => {
        const matched = data.keywords || [];

        keywordList.innerHTML = "";
        const showBtn = document.getElementById("show-keywords-btn");

        if (matched.length > 0) {
            matched.forEach(keyword => {
                const li = document.createElement("li");
                li.textContent = keyword;
                li.classList.add("found-keyword");
                keywordList.appendChild(li);
            });

            showBtn.style.display = "inline-block";

        } else {
            const li = document.createElement("li");
            //li.textContent = "No keywords found";
            //li.style.color = "#555";
            li.classList.add("no-keywords");
            keywordList.appendChild(li);
            showBtn.style.display = "inline-block";
        }

        updateDiagnosisWithTests(matched);
    })
    .catch(error => {
        console.error("Keyword extraction failed:", error);
        alert("Something went wrong while extracting symptoms.");
    })
    .finally(() => {
        // Hide spinner in both success and error cases
        spinner.classList.remove("active");
    });
}

document.addEventListener("DOMContentLoaded", fetchBaseline);

// Modal logic
const modal = document.getElementById('keywords-modal');
const modalList = document.getElementById('modal-keyword-list');
const showBtn = document.getElementById('show-keywords-btn');
const closeBtn = document.getElementById('close-modal-btn');

showBtn.addEventListener('click', () => {
    const keywordList = document.getElementById('modal-keyword-list');

    // Clone list items from the main UI
    modalList.innerHTML = keywordList.innerHTML;

    // Show the modal
    modal.style.display = 'flex';
});

closeBtn.addEventListener('click', () => {
    modal.style.display = 'none';
});

// Optional: click outside modal content to close
modal.addEventListener('click', (e) => {
    if (e.target === modal) {
        modal.style.display = 'none';
    }
});

const textarea = document.getElementById("symptom-input");

textarea.addEventListener("input", () => {
  textarea.style.height = "auto"; // Reset height to shrink if needed
  textarea.style.height = Math.min(textarea.scrollHeight, 300) + "px"; // Grow up to 200px
});

# Hortonian Infiltration

![HortonianGif](https://github.com/user-attachments/assets/4c563802-a8ae-4a62-b712-bcc77ad8ce80)

Based on Thomas Reimann's <a href = "https://github.com/gw-inux/Jupyter-Notebooks/tree/main/02_Basic_hydrology">Jupyter Notebook</a>, this application explores soil infiltration rate as a function of time, infiltration capacity and precipitation rate, using <a href="https://acsess.onlinelibrary.wiley.com/doi/10.2136/sssaj1941.036159950005000C0075x">Horton's 1940</a> soil infiltration model:</p>
<br>
<p class="equation">$$ f_p = f_c + (f_0 - f_c) e^{-kt}$$</p>
<br>
<p class="text">with:</p>
<ul class="bullets">
<li>$ f_p $ = infiltration rate (cm/hr)</li>
<li>$f_c$ = equilibrium infiltration capacity (cm/hr)</li>
<li>$f_0$ = initial infiltration capacity (cm/hr)</li>
<li>$k$ = infiltration capacity decrease coefficient (1/hr)</li>
<li>$t$ = time (hr)</li>
</ul>
</head>

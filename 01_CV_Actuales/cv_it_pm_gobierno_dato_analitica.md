<style>
  :root {
    --text-normal: #1e293b;
    --text-muted: #475569;
    --text-accent: #1e40af; /* Deep Executive Blue */
    --text-accent-hover: #1e3a8a;
    --background-secondary: #f8fafc;
    --background-accent-light: rgba(30, 64, 175, 0.06);
    --text-title-h1: #0f172a;
    --border-color: #cbd5e1;
    --highlight-border: #1e40af;
  }
  #cv {
    font-family: 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: var(--text-normal);
    line-height: 1.5;
    max-width: 68rem;
    margin: 1.5rem auto;
    background: white;
    padding: 2.25rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    border-radius: 0.75rem;
  }
  .cv-header {
    display: grid;
    grid-template-columns: auto 1fr;
    align-items: center;
    column-gap: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 3px solid var(--text-accent);
    margin-bottom: 1.5rem;
  }
  .cv-profile-pic {
    width: 7.5rem;
    height: 7.5rem;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid var(--background-secondary);
    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
  }
  .cv-header-text h1 {
    margin: 0;
    font-size: 2.4rem;
    font-weight: 800;
    letter-spacing: -0.04rem;
    color: var(--text-title-h1);
    line-height: 1.1;
  }
  .cv-subtitle {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text-accent);
    margin: 0.4rem 0 0.8rem 0;
  }
  .cv-contact {
    display: flex;
    gap: 1.25rem;
    flex-wrap: wrap;
    font-size: 0.88rem;
  }
  .cv-contact a {
    text-decoration: none;
    color: var(--text-muted);
    font-weight: 600;
    transition: color 0.2s ease;
  }
  .cv-contact a:hover {
    color: var(--text-accent);
  }
  .cv-content {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  .cv-section-title {
    font-size: 1.2rem;
    font-weight: 700;
    border-bottom: 2px solid var(--border-color);
    padding-bottom: 0.4rem;
    margin-top: 1.5rem;
    margin-bottom: 1rem;
    color: var(--text-title-h1);
    text-transform: uppercase;
    letter-spacing: 0.05rem;
  }
  .cv-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
  }
  .cv-job {
    margin-bottom: 1.25rem;
    padding-bottom: 1.25rem;
    border-bottom: 1px dashed var(--border-color);
  }
  .cv-job:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
  }
  .cv-job-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 0.25rem;
  }
  .cv-job-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-title-h1);
  }
  .cv-job-company {
    font-weight: 600;
    color: var(--text-accent);
    font-size: 0.95rem;
    margin-bottom: 0.4rem;
  }
  .cv-job-date {
    font-size: 0.82rem;
    color: var(--text-muted);
    font-weight: 600;
    background-color: var(--background-secondary);
    padding: 0.15rem 0.5rem;
    border-radius: 0.25rem;
  }
  .cv-job ul {
    margin-top: 0.4rem;
    margin-bottom: 0;
    padding-left: 1.25rem;
  }
  .cv-job li {
    margin-bottom: 0.3rem;
    font-size: 0.9rem;
  }
  .cv-job p {
    margin: 0.4rem 0;
    font-size: 0.9rem;
  }
  .fit-box {
    background-color: var(--background-accent-light);
    border-left: 4px solid var(--highlight-border);
    padding: 1rem 1.25rem;
    font-size: 0.92rem;
    margin-bottom: 1rem;
    border-radius: 0 0.5rem 0.5rem 0;
  }
  .fit-box strong {
    color: var(--text-accent);
  }
  .badge-container {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-top: 0.6rem;
  }
  .badge {
    background-color: #eff6ff;
    color: #1e40af;
    border: 1px solid #bfdbfe;
    padding: 0.2rem 0.5rem;
    border-radius: 0.375rem;
    font-size: 0.78rem;
    font-weight: 700;
  }
  .skills-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
    gap: 0.85rem;
    margin-top: 0.4rem;
  }
  .skill-card {
    background-color: var(--background-secondary);
    padding: 0.85rem;
    border-radius: 0.5rem;
    border: 1px solid var(--border-color);
  }
  .skill-card h4 {
    margin: 0 0 0.4rem 0;
    color: var(--text-accent);
    font-size: 0.95rem;
    font-weight: 700;
  }
  .skill-card ul {
    margin: 0;
    padding-left: 1.1rem;
  }
  .skill-card li {
    font-size: 0.82rem;
    margin-bottom: 0.2rem;
  }
  /* Mobile screen support */
  @media screen and (max-width: 48rem) {
    #cv {
      padding: 1.25rem;
      margin: 0 auto;
      box-shadow: none;
    }
    .cv-header {
      grid-template-columns: 1fr;
      text-align: center;
      justify-items: center;
      row-gap: 1.25rem;
    }
    .cv-contact {
      justify-content: center;
    }
    .cv-job-header {
      flex-direction: column;
      gap: 0.2rem;
      align-items: flex-start;
    }
    .cv-grid {
      grid-template-columns: 1fr;
    }
  }
  /* PDF Print Optimizations */
  @media print {
    @page { margin: 1cm 1.2cm; }
    html { font-size: 9pt; }
    #cv {
      padding: 0;
      margin: 0;
      box-shadow: none;
      max-width: none;
    }
    .cv-job {
      page-break-inside: avoid;
      break-inside: avoid;
    }
    .fit-box, .skill-card {
      page-break-inside: avoid;
      break-inside: avoid;
    }
  }
</style>

<div id="cv">
  <div class="cv-header">
    <img src="images/profile-img.jpg" alt="Gabriel Rul-lan" class="cv-profile-pic">
    <div class="cv-header-text">
      <h1>Gabriel Rul-lan</h1>
      <div class="cv-subtitle">IT Project Manager | Gobierno del Dato & Analítica Avanzada</div>
      <div class="cv-contact">
        <a href="http://data-partner.xyz">🌐 data-partner.xyz</a>
        <a href="mailto:gabriel@data-partner.xyz">📧 gabriel@data-partner.xyz</a>
        <a href="tel:+34638952623">📱 +34 638 95 26 23</a>
        <span>📍 España (100% Remoto)</span>
      </div>
      <div class="badge-container">
        <span class="badge">🎓 Certificado PMP® (PMI)</span>
        <span class="badge">📊 Especialista DAMA-DMBOK</span>
        <span class="badge">💼 Freelance / Contractor</span>
        <span class="badge">⚡ Disponibilidad Inmediata</span>
      </div>
    </div>
  </div>

  <div class="cv-content">
    
    <!-- Propuesta de Valor alineada con la Oferta laboral -->
    <div class="fit-box">
      <strong>🎯 PERFIL Y PROPUESTA DE VALOR PARA LA OFERTA:</strong><br>
      <strong>IT Project Manager Senior</strong> con más de <strong>13 años de experiencia</strong> en la dirección y ejecución de proyectos de <strong>Gobierno del Dato</strong> y <strong>Analítica Avanzada / Business Intelligence</strong>. Certificado <strong>PMP® (Project Management Institute)</strong> y experto en marcos internacionales de gestión de datos (<strong>DAMA-DMBOK</strong>). Amplio bagaje en grandes corporaciones internacionales (AstraZeneca, Mapfre, Boehringer Ingelheim, APSL) liderando equipos multidisciplinares, alineando necesidades de negocio con desarrollos técnicos y asegurando entregas a tiempo y en presupuesto.
      <br><br>
      <strong>Modalidad:</strong> Freelance / Contractor | 100% Remoto desde España | <strong>Disponibilidad inmediata para incorporación urgente.</strong>
    </div>

    <!-- Habilidades Clave alineadas con la oferta -->
    <div>
      <h2 class="cv-section-title">Competencias Clave (Alineadas con la Oferta)</h2>
      <div class="skills-container">
        <div class="skill-card">
          <h4>Dirección de Proyectos IT</h4>
          <ul>
            <li><strong>Certificación PMP® (PMI)</strong></li>
            <li>Metodologías Ágiles (Scrum, Kanban) y Cascada</li>
            <li>Gestión de Alcance, Tiempos, Riesgos y Costes</li>
            <li>Liderazgo de Equipos Multidisciplinares</li>
            <li>Gestión de Stakeholders y C-Level</li>
          </ul>
        </div>
        <div class="skill-card">
          <h4>Gobierno del Dato (Data Governance)</h4>
          <ul>
            <li><strong>Marco DAMA-DMBOK</strong></li>
            <li>Creación de Data Domain Working Groups (DDWGs)</li>
            <li>Roles (Data Owners, Data Stewards, Custodians)</li>
            <li>Elementos Críticos de Datos (CDEs) y Catálogos</li>
            <li>Gobernanza de IA y Cumplimiento de Datos</li>
          </ul>
        </div>
        <div class="skill-card">
          <h4>Analítica Avanzada & BI</h4>
          <ul>
            <li>Proyectos de Analytics & Machine Learning</li>
            <li>Dashboards Ejecutivos y Reporting Dinámico</li>
            <li>Estrategias de Arquitectura y Target Operating Models</li>
            <li>Preparación para Enterprise Data Quality Tools</li>
            <li>Power BI, Looker, BigQuery, SQL, dbt</li>
          </ul>
        </div>
        <div class="skill-card">
          <h4>Visión de Negocio & Autonomía</h4>
          <ul>
            <li>Business Analysis & Traducción Negocio-Técnica</li>
            <li>Modelos de Prestación Freelance / Remoto</li>
            <li>Toma de Decisiones y Autonomía de Gestión</li>
            <li>Gestión del Cambio y Habilitación de Usuarios</li>
            <li>Comunicación Ejecutiva y Presentaciones</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Salto de Página Forzado -->
    <div class="page-break" style="page-break-before: always; break-before: page;"></div>

    <!-- Experiencia Profesional Relevante -->
    <div>
      <h2 class="cv-section-title">Experiencia Profesional Relevante</h2>

      <div class="cv-job">
        <div class="cv-job-header">
          <div class="cv-job-title">Associate Director, R&D Data Governance & Project Lead</div>
          <span class="cv-job-date">Mayo 2024 - Presente</span>
        </div>
        <div class="cv-job-company">AstraZeneca</div>
        <p>Dirección y liderazgo del programa de madurez del Gobierno de Datos e interoperabilidad de información en dominios críticos globales de I+D.</p>
        <ul>
          <li><strong>Gestión de Proyectos y Gobernanza:</strong> Liderazgo del despliegue de Data Domain Working Groups (DDWGs), definiendo principios rectores, entregables, roles y responsabilidades de gobernanza a nivel corporativo.</li>
          <li><strong>Gobierno y Calidad del Dato:</strong> Coordinación de la identificación y priorización de Elementos Críticos de Datos (CDEs), implantación de catálogos de datos y preparación operacional para herramientas corporativas de calidad de datos.</li>
          <li><strong>Gestión de Stakeholders:</strong> Facilitación del consenso entre directivos de negocio, data owners y equipos de tecnología para alinear los hitos del proyecto con la estrategia global.</li>
        </ul>
      </div>

      <div class="cv-job">
        <div class="cv-job-header">
          <div class="cv-job-title">Head of Data & IT Project Manager</div>
          <span class="cv-job-date">Septiembre 2023 - Marzo 2024</span>
        </div>
        <div class="cv-job-company">Start-up (Stealth Mode)</div>
        <p>Dirección estratégica del área de datos y gestión de proyectos tecnológicos para la construcción de una plataforma analítica avanzada basada en IA.</p>
        <ul>
          <li><strong>Estrategia y Roadmap:</strong> Definición e implantación del Modelo Operativo Objetivo (Target Operating Model) y planificación del roadmap de iniciativas analíticas a corto y medio plazo.</li>
          <li><strong>Analítica Avanzada y Gobernanza de IA:</strong> Liderazgo en el diseño de algoritmos de analítica avanzada y en la implantación de marcos de gobernanza de Inteligencia Artificial (ética, trazabilidad y calidad del dato).</li>
          <li><strong>Gestión de Proyectos:</strong> Gestión del equipo técnico de desarrollo, priorización del backlog y reporte directo al C-Level.</li>
        </ul>
      </div>

      <div class="cv-job">
        <div class="cv-job-header">
          <div class="cv-job-title">Data Partner & Solutions Project Expert</div>
          <span class="cv-job-date">Enero 2023 - Junio 2023</span>
        </div>
        <div class="cv-job-company">Mapfre</div>
        <p>Liderazgo y ejecución directa de proyectos de transformación en la gestión e interacción analítica de datos para el área de Contact Center.</p>
        <ul>
          <li><strong>Gestión Autónomo de Proyectos:</strong> Planificación, coordinación y desarrollo 100% independiente de soluciones analíticas sin sobrecargar el equipo core de datos de la compañía.</li>
          <li><strong>Analítica y Soluciones:</strong> Despliegue de modelos analíticos en BigQuery, LookerML y SQL, optimizando los procesos operativos y de toma de decisiones del área.</li>
        </ul>
      </div>

      <div class="cv-job">
        <div class="cv-job-header">
          <div class="cv-job-title">Dynamic Data Specialist / Project Lead - Internal Auditing</div>
          <span class="cv-job-date">Abril 2022 - Diciembre 2022</span>
        </div>
        <div class="cv-job-company">Boehringer Ingelheim</div>
        <p>Liderazgo de proyectos analíticos y de auditoría interna de datos en un entorno altamente regulado.</p>
        <ul>
          <li><strong>Analítica Avanzada y Cumplimiento:</strong> Desarrollo y coordinación de soluciones para el análisis masivo de datos orientado a evaluar el cumplimiento normativo y políticas corporativas.</li>
          <li><strong>Entrega de Dashboards:</strong> Dirección del diseño e implantación de más de 30 cuadros de mando analíticos en Power BI para control global.</li>
        </ul>
      </div>

      <div class="cv-job">
        <div class="cv-job-header">
          <div class="cv-job-title">Data Platform Lead & Senior Consultant</div>
          <span class="cv-job-date">Marzo 2021 - Abril 2022</span>
        </div>
        <div class="cv-job-company">Movinga</div>
        <p>Gestión del proyecto de refactorización de la plataforma de datos e implantación de principios de Master Data Management (MDM).</p>
        <ul>
          <li><strong>Calidad y Gobierno:</strong> Rediseño de pipelines ETL (dbt, Python, Talend) garantizando la calidad, integridad y gobernanza del dato.</li>
          <li><strong>Gestión de Equipos:</strong> Mentoring y coordinación de 4 ingenieros junior para asegurar la transferencia de conocimiento y continuidad operativa.</li>
        </ul>
      </div>

      <div class="cv-job">
        <div class="cv-job-header">
          <div class="cv-job-title">IT Project Manager & Analytics Specialist</div>
          <span class="cv-job-date">Agosto 2016 - Octubre 2020</span>
        </div>
        <div class="cv-job-company">Advanced Programming Solutions SL (APSL)</div>
        <p>Gestión de proyectos tecnológicos y dirección de equipos de desarrollo en proyectos de analítica avanzada, Business Intelligence y soluciones software.</p>
        <ul>
          <li><strong>Project Management (PMP):</strong> Gestión integral del ciclo de vida del proyecto (planificación de hitos, estimaciones, control de riesgos, metodología Ágil/Scrum).</li>
          <li><strong>Business Analyst & Key Account Manager:</strong> Nexo clave entre las áreas de negocio y el equipo técnico de desarrollo, traduciendo requisitos funcionales en arquitecturas y entregables técnicos.</li>
        </ul>
      </div>

      <div class="cv-job">
        <div class="cv-job-header">
          <div class="cv-job-title">Business Intelligence Senior Consultant / Project Lead</div>
          <span class="cv-job-date">Julio 2014 - Febrero 2016</span>
        </div>
        <div class="cv-job-company">SDG Group Spain</div>
        <p>Liderazgo y desarrollo de proyectos BI para grandes multinacionales farmacéuticas (cuadros de mando, reporting periódico, arquitectura QlikView).</p>
      </div>

    </div>

    <!-- Educación y Certificaciones -->
    <div class="cv-grid">
      <div>
        <h2 class="cv-section-title">Certificaciones y Formación</h2>
        <ul>
          <li>🎓 <strong>Project Management Professional (PMP®)</strong> – PMI</li>
          <li>📊 <strong>Marco de Gobierno y Gestión de Datos</strong> (DAMA-DMBOK)</li>
          <li>🎓 <strong>Máster en Dirección de Empresas (MBA)</strong> – ESERP (2014)</li>
          <li>🎓 <strong>Licenciatura en Matemáticas</strong> – UIB (2013)</li>
        </ul>
      </div>
      <div>
        <h2 class="cv-section-title">Idiomas y Modalidad</h2>
        <ul>
          <li>🗣️ <strong>Español:</strong> Nativo</li>
          <li>🗣️ <strong>Inglés:</strong> Profesional (Lectura C1, Conversación B2)</li>
          <li>💼 <strong>Modalidad:</strong> Freelance / Contractor (100% Remoto)</li>
          <li>⚡ <strong>Disponibilidad:</strong> Inmediata</li>
        </ul>
      </div>
    </div>

  </div>
</div>

import Analyzer from "./Analyzer";
import "./styles.css";


function App() {

  return (

    <div className="app">

      <header className="header">

        <div className="header-content">

          <h1>
            AI Resume Analyzer
          </h1>

          <p>
            Understand how well your resume matches
            a job and discover what you can improve.
          </p>

        </div>

      </header>


      <main className="container">

        <Analyzer />

      </main>

    </div>

  );

}


export default App;
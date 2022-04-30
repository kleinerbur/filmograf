import logo from './logo.svg';
import './App.css';
import DepthSlider from './components/DepthSlider';
import SearchBar from './components/SearchBar';
import FilmGraph from './components/FilmGraph';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        {/* <img src={logo} className="App-logo" alt="logo" /> */}
        {/* <h1 style={{fontFamily: "Bahnschrift", fontWeight: "lighter"}}>film-o-gráf</h1> */}
        
        <form id='settings'>
          <SearchBar
            label='Színész / film'
            variant='filled'
            size='small'
            color='secondary'
            required/>
            {/* error helperText="Nincs ilyen színész / film az adatbázisban."/>  */}
          <DepthSlider
            aria-label='asdasd'
            valueLabelDisplay='auto'
            min={0} max={3} marks/>
        </form>
        {/* <div id='network'>
          <FilmGraph/>
        </div> */}
      </header>
    </div>
  );
}

export default App;

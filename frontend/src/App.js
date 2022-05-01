import logo from './logo.svg';
import './App.css';
import DepthSlider from './components/DepthSlider';
import SearchBar from './components/SearchBar';
import FilmGraph from './components/FilmGraph';
import { sliderClasses } from '@mui/material';

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
        
          <DepthSlider id='slider'
            aria-label='asdasd'
            valueLabelDisplay='auto'
            min={0} max={3} marks/>
        
        </form>
          <FilmGraph mode='graph' root='Emma Stone' depth='2'/>
      </header>
    </div>
  );
}

export default App;

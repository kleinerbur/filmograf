import Slider from '@mui/material/Slider';
import { styled } from '@mui/material/styles';

const DepthSlider = styled(Slider)({
    marginTop: 65,

    color: 'white',
    height: 8,
    width: 400,
    
    '& .MuiSlider-label': {
      color: '#eee',
      border: '1px solid #eee',
    },
    
    '& .MuiSlider-track': {
      color: '#eee',
      border: '1px solid #eee',
    },
    
    '& .MuiSlider-thumb': {
      height: 22,
      width: 22,
      borderRadius: '0 0 0 0',

      transformOrigin: 'bottom left',
      transform: 'rotate(45deg) translate(-115%, -25%)',
      backgroundColor: 'white',

      '&:focus, &:hover, &.Mui-active, &.Mui-focusVisible': {
        boxShadow: 'inherit',
      },

      '&:before': {
        display: 'none',
      },
    },
    
    '& .MuiSlider-valueLabel': {
      fontSize: 25,
      fontWeight: 'bold',
      fontFamily: 'Bahnschrift',
      background: 'none',

      padding: 0,
      margin: 0,
      width: 32,
      height: 32,
      
      color: 'white',
      opacity: 0.6,
      transition: 'opacity 0.25s ease-in-out',
      transformOrigin: 'bottom left',
      transform: 'rotate(-90deg) translate(85%, 0%)',
      
      '&:before': { display: 'none' },
      '&.MuiSlider-valueLabelOpen': {
        transform: 'rotate(-90deg) translate(85%, 0%) scale(1)',
        opacity: 1,
        transition: 'opacity 0.25s ease-in-out',
      },
      '& > *': {
        transform: 'rotate(45deg)',
      },
    },
  });

export default DepthSlider;
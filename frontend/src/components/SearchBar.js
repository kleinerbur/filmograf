import TextField from '@mui/material/TextField';
import { styled } from '@mui/material/styles';

const SearchBar = styled(TextField)({
    fontFamily: 'Bahnschrift',
    fontSize: '15pt',
    color: 'white',
    variant: 'standard',
    width: 400,
    '& label': {
        fontFamily: 'Bahnschrift',
    },
    '& label.Mui-focused': {
        color: 'white',
        fontFamily: 'Bahnschrift',
    },
    input: {
        color: 'white'
    },
});

export default SearchBar;
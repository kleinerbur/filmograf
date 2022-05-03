import TextField from '@mui/material/TextField';
import { styled } from '@mui/material/styles';
import React from 'react';

const defaultStyle = {
    minWidth: 400,
    maxWidth: 400,
    fontFamily: 'Bahnschrift',
    fontSize: '15pt',
    color: 'white',
    '& label': {
        fontFamily: 'Bahnschrift',
    },
    '& label.Mui-focused': {
        color: 'white',
        fontFamily: 'Bahnschrift',
    },
    input: {
        color: 'white'
    }
}

const API_URL = 'http://127.0.0.1:8000/api/'


class SearchBar extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            name: props.name,
            label: props.label,
            value: props.value,
            onChange: props.onChange,   

            error: false,
            helperText: '',
            hidden: props.hidden
        }
    }

    error(helperText) {
        this.setState({
            error: true,
            helperText: helperText
        })
    }

    clearError() {
        this.setState({
            error: false,
            helperText: ''
        })
    }

    render() {
        if (this.state.hidden) return (<></>)
        return (<TextField
                    id={this.state.name}
                    name={this.state.name}
                    label={this.state.label}
                    
                    variant='filled'
                    color='secondary'
                    type="text"
                    sx={defaultStyle}
                    
                    hidden={this.state.hidden}

                    error={this.state.error}
                    helperText={this.state.helperText}
                    
                    onChange={this.state.onChange}/>)
    }
}

export default SearchBar;
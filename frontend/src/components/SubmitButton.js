import IconButton from '@mui/material/IconButton';
import KeyboardArrowRightIcon from '@mui/icons-material/KeyboardArrowRight';
import React from 'react';

const defaultSx = {
    fontFace: 'Bahnschrift',
    fontWeight: 'bold',
    backgroundColor: '#4da570',
    color: '#1f4637',
    fontSize: 15,
    border: '0px solid red',
    borderRadius: 0,
    transform: 'rotate(45deg)',
    padding: '5px',

    ':hover': {
        border: '0px solid red',
        backgroundColor: 'white',
        color: '#1f4637'
    },
};


class SubmitButton extends React.Component {
    constructor(props) {
        super(props)
        this.state = {form: props.form}
    }

    render() {
        return (<IconButton
                    type='reset'
                    variant='contained'
                    form={this.state.form}
                    sx={defaultSx}>
                        <KeyboardArrowRightIcon 
                            sx={{
                                width: 35,
                                height: 35,
                                transform: 'rotate(-45deg)',                            
                            }}/>
                </IconButton>
        )
    }
}

export default SubmitButton;
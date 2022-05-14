const APP_URI = 'http://localhost:3000'

describe('UI test', () => {
    it('Switching between modes', () => {
        cy.visit(APP_URI)

        cy.get('#path-button').should('be.enabled')
        cy.get('#graph-button').should('be.disabled')
        cy.get('#left').should('exist')
        cy.get('#right').should('not.exist')
        cy.get('#depth').should('exist')

        cy.get('#path-button').click()
        cy.wait(100)

        cy.get('#path-button').should('be.disabled')
        cy.get('#graph-button').should('be.enabled')
        cy.get('#left').should('exist')
        cy.get('#right').should('exist')
        cy.get('#depth').should('not.exist')

        cy.get('#graph-button').click()
        cy.wait(100)

        cy.get('#path-button').should('be.enabled')
        cy.get('#graph-button').should('be.disabled')
        cy.get('#left').should('exist')
        cy.get('#right').should('not.exist')
        cy.get('#depth').should('exist')
    })

    it('Open help drawer', () => {
        cy.visit(APP_URI)
        cy.get('.help-panel').should('not.exist')

        cy.get('#help').click()
        cy.wait(100)

        cy.get('.help-panel').should('be.visible')
        cy.get('body').click('left')
        cy.get('.help-panel').should('be.visible')

        cy.get('body').click('right')
        cy.wait(100)

        cy.get('.help-panel').should('not.exist')
    })

    it('Input validation', () => {
        cy.visit(APP_URI)
        cy.get('#submit-button').should('be.disabled')
        cy.get('#left').type('tom hanks', {delay: 20})
        cy.wait(700)
        
        cy.get('#left-helper-text').should('not.exist')
        cy.get('#submit-button').should('be.enabled')
        cy.get('#path-button').click()
        cy.wait(700)

        cy.get('#right').type('aaa', {delay: 20})
        cy.wait(700)

        cy.get('#right-helper-text').should('exist')
        cy.contains('Nincs ilyen színész / film az adatbázisban!')
        cy.get('#submit-button').should('be.disabled')
        cy.get('#right').clear()        
        cy.get('#right').type('nm0000158')
        cy.wait(700)

        cy.get('#right-helper-text').should('not.exist')
        cy.get('#submit-button').should('be.enabled')
        cy.get('#right').clear()
        cy.get('#right').type('https://www.imdb.com/name/nm0000158/')
        cy.wait(700)

        cy.get('#right-helper-text').should('not.exist')
        cy.get('#submit-button').should('be.enabled')
    })

    it('Slider', () => {
        cy.visit(APP_URI)

        cy.get('#depth').should('exist')
        cy.get('span[data-index=1]').click()
        cy.wait(100)
        cy.get('span[data-index=2]').click()
        cy.wait(100)
        cy.get('span[data-index=3]').click()
        cy.wait(100)
        cy.get('span[data-index=4]').click()
        cy.wait(100)
        cy.get('span[data-index=3]').click()
        cy.wait(100)
        cy.get('span[data-index=2]').click()
        cy.wait(100)
        cy.get('span[data-index=1]').click()
        cy.wait(100)
        cy.get('span[data-index=0]').first().click()
    })

    it('Submit and open info panel', () => {
        cy.visit(APP_URI)

        cy.get('#left').type('tom hanks', {delay:20})
        cy.wait(1000)

        cy.get('#submit-button').click()
        cy.wait(500)

        cy.get('body').click(850, 520)
        cy.get('body').dblclick(850, 520)
        cy.wait(200)

        cy.get('.info-panel').should('exist')
        cy.get('.poster').should('exist')
        cy.get('.imdb-button').should('exist')
        cy.get('.imdb-button').click()
        cy.wait(200)

        cy.get('body').click('left')
    })
})
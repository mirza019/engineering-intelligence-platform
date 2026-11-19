import{render,screen}from'@testing-library/react';import{describe,expect,it}from'vitest';import{App}from'./App';
describe('App',()=>{it('renders governed dashboard',()=>{render(<App/>);expect(screen.getByText('Engineering intelligence, governed.')).toBeTruthy()})});

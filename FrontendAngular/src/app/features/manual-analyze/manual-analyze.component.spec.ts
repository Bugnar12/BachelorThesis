import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ManualAnalyzeComponent } from './manual-analyze.component';

describe('ManualAnalyzeComponent', () => {
  let component: ManualAnalyzeComponent;
  let fixture: ComponentFixture<ManualAnalyzeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ManualAnalyzeComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ManualAnalyzeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

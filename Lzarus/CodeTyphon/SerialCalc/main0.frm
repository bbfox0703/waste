object Form1: TForm1
  Left = 292
  Height = 453
  Top = 207
  Width = 570
  Caption = 'StrEnc (20180502)'
  ClientHeight = 453
  ClientWidth = 570
  OnCreate = FormCreate
  LCLVersion = '6.3'
  object Button1: TButton
    Left = 96
    Height = 25
    Top = 16
    Width = 75
    Caption = 'Single Row'
    OnClick = Button1Click
    TabOrder = 0
  end
  object Edit1: TEdit
    Left = 96
    Height = 24
    Top = 48
    Width = 296
    TabOrder = 1
    Text = 'Input data here'
  end
  object Edit2: TEdit
    Left = 96
    Height = 24
    Top = 80
    Width = 296
    EchoMode = emPassword
    Enabled = False
    PasswordChar = '#'
    ReadOnly = True
    TabOrder = 2
  end
  object Edit4: TEdit
    Left = 96
    Height = 24
    Top = 112
    Width = 296
    ReadOnly = True
    TabOrder = 3
  end
  object Label1: TLabel
    Left = 22
    Height = 12
    Top = 60
    Width = 60
    Caption = 'SourceString'
    ParentColor = False
  end
  object Label2: TLabel
    Left = 22
    Height = 12
    Top = 92
    Width = 50
    Caption = 'MD5 Hash'
    ParentColor = False
  end
  object Label3: TLabel
    Left = 22
    Height = 12
    Top = 124
    Width = 23
    Caption = 'Final'
    ParentColor = False
  end
  object Memo1: TMemo
    Left = 96
    Height = 216
    Top = 192
    Width = 224
    Lines.Strings = (
      'Data1'
      'Data2'
      '.....'
    )
    ScrollBars = ssAutoVertical
    TabOrder = 4
    WordWrap = False
  end
  object Memo2: TMemo
    Left = 336
    Height = 216
    Top = 192
    Width = 216
    ReadOnly = True
    ScrollBars = ssAutoVertical
    TabOrder = 5
    WordWrap = False
  end
  object Button2: TButton
    Left = 96
    Height = 25
    Top = 160
    Width = 75
    Caption = 'Multi Row'
    OnClick = Button2Click
    TabOrder = 6
  end
end

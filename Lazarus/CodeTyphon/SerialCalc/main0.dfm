object Form1: TForm1
  Left = 0
  Top = 0
  Caption = 'Serial -> password simple generator'
  ClientHeight = 194
  ClientWidth = 540
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  PixelsPerInch = 96
  TextHeight = 13
  object Label1: TLabel
    Left = 56
    Top = 115
    Width = 21
    Height = 13
    Caption = 'MD5'
  end
  object Label2: TLabel
    Left = 56
    Top = 155
    Width = 46
    Height = 13
    Caption = 'Password'
  end
  object Label3: TLabel
    Left = 56
    Top = 75
    Width = 65
    Height = 13
    Caption = 'Serial number'
  end
  object Label4: TLabel
    Left = 296
    Top = 29
    Width = 225
    Height = 13
    Caption = 'Example for generate BIOS password from S/N'
  end
  object Button1: TButton
    Left = 56
    Top = 24
    Width = 75
    Height = 25
    Caption = 'Calculate'
    TabOrder = 0
    OnClick = Button1Click
  end
  object Edit1: TEdit
    Left = 127
    Top = 112
    Width = 394
    Height = 21
    TabOrder = 1
  end
  object Edit2: TEdit
    Left = 127
    Top = 152
    Width = 394
    Height = 21
    TabOrder = 2
  end
  object Edit3: TEdit
    Left = 127
    Top = 72
    Width = 394
    Height = 21
    TabOrder = 3
  end
end

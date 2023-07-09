1 using Ardalis.GuardClauses;
2 using AutoMapper;
3 using Domain.Dtos;
4 using Domain.Entities;
5 using Infrastructure.Authorisation;
6 using Infrastructure.Exceptions;
7 using Infrastructure.Persistence;
8 using Infrastructure.Services.DataContracts.UbiPark;
9 using Infrastructure.Util;
10 using Microsoft.EntityFrameworkCore;
11 using Microsoft.Extensions.Logging;
12 
13 namespace Infrastructure.Services;
14 
15 public class CarParkService : ICarParkService
16 {
17     private readonly IUbiParkDataAccessService _ubiParkDataAccessService;
18     private readonly UserIdentity _userIdentity;
19     private readonly ApplicationDatabaseContext _dbContext;
20     private readonly IGuidProvider _guidProvider;
21     private readonly IMapper _mapper;
22     private readonly ILogger<CarParkService> _logger;
23 
24     public CarParkService(
25         UserIdentity userIdentity,
26         ApplicationDatabaseContext dbContext,
27         IUbiParkDataAccessService ubiParkDataAccessService,
28         IMapper mapper,
29         IGuidProvider guidProvider,
30         ILogger<CarParkService> logger)
31     {
32         _ubiParkDataAccessService = ubiParkDataAccessService;
33         _userIdentity = userIdentity;
34         _dbContext = dbContext;
35         _guidProvider = guidProvider;
36         _mapper = mapper;
37         _logger = logger;
38 
39     }
40 
41     public async Task<IList<CarParkProductDto>> GetProductsAsync(CarParkProductSearchRequestDto carParkSearchRequest, CancellationToken cancellationToken)
42     {
43         var availabilityRequest = new ProductAvailableRequest
44         {
45             EffectiveFrom = carParkSearchRequest.EntryFrom,
46             EffectiveTo= carParkSearchRequest.ExitBy,
47             PromoCode = carParkSearchRequest.PromoCode
48         };
49         _logger.LogInformation("Initiating car parking request for {carParkRequestEntryDate}", carParkSearchRequest.EntryFrom);
50 
51         var result = await _ubiParkDataAccessService.AvailableCarParkProductsList(availabilityRequest, cancellationToken);
52         if (!result.Success || result.Products == null)
53         {
54             _logger.LogWarning("Car parking request did not return availability for {carParkRequestEntryDate}", carParkSearchRequest.EntryFrom);
55             return new List<CarParkProductDto>();
56         }
57         var carProducts = result.Products.Where(p => p.Result).Select(cp => _mapper.Map<CarParkProductDto>(cp)).ToList();
58         //re-populate promoCode value as currently response does not return sent in request promo code
59         carProducts.ForEach(p => p.PromoCode = carParkSearchRequest.PromoCode!);
60         return carProducts.ToList();
61     }
62 
63     public async Task<CarParkUserDetails> ObtainUserAsync(CancellationToken cancellationToken)
64     {
65         var ubiParkUserId =
66             (await _dbContext.CarParkUserInfo
67             .SingleOrDefaultAsync(u => u.UserId == _userIdentity.UserId, cancellationToken))?
68             .UbiparkUserId;
69 
70         // Create user if not exists
71         if (string.IsNullOrEmpty(ubiParkUserId)) return await CreateUser(cancellationToken);
72 
73         // Get user if exists, Update user if information has changed and return
74         var existingCarParkUser = await GetUser(ubiParkUserId, cancellationToken);
75         if (UserInformationHasChanged(existingCarParkUser)) await UpdateUser(existingCarParkUser, cancellationToken);
76 
77         return existingCarParkUser;
78     }
79 
80     private async Task<CarParkUserDetails> CreateUser(CancellationToken cancellationToken)
81     {
82         var request = new CreateUserRequest
83         {
84             UserID = _guidProvider.NewGuid.ToString(),
85             Email = _userIdentity.Email,
86             FirstName = _userIdentity.FirstName,
87             LastName = _userIdentity.LastName,
88             PhoneNo = _userIdentity.MobilePhone
89         };
90 
91         _logger.LogInformation("Create user {UserId}", request.UserID);
92 
93         var result = await _ubiParkDataAccessService.CreateUser(request, cancellationToken);
94 
95         if (!result.Success)
96         {
97             var errors = string.Join(',', result.Errors);
98             throw new CarParkServiceException($"Failed to create user {request.UserID}. Errors: {errors}");
99         }
100 
101         _dbContext.CarParkUserInfo.Add(new CarParkUserInfo
102         {
103             UserId = _userIdentity.UserId,
104             UbiparkUserId = result.UserID
105         });
106 
107         await _dbContext.SaveChangesAsync(cancellationToken);
108 
109         return new CarParkUserDetails
110         {
111             UserId = result.UserID,
112             Email = _userIdentity.Email,
113             FirstName = _userIdentity.FirstName,
114             LastName = _userIdentity.LastName,
115             PhoneNo = _userIdentity.MobilePhone,
116             CardToken = result.CardToken,
117             PublishableKey = result.PublishableKey
118         };
119     }
120 
121     private async Task<CarParkUserDetails> GetUser(string ubiParkUserId, CancellationToken cancellationToken)
122     {
123         _logger.LogInformation("Get information about user {UserId}", ubiParkUserId);
124 
125         var result = await _ubiParkDataAccessService.GetUser(new UserRequest { UserID = ubiParkUserId }, cancellationToken);
126 
127         if (!result.Success)
128         {
129             var errors = string.Join(',', result.Errors);
130             throw new CarParkServiceException($"Failed to get user {ubiParkUserId}. Errors: {errors}");
131         }
132 
133         return new CarParkUserDetails
134         {
135             UserId = ubiParkUserId,
136             Email = result.Email,
137             FirstName = result.FirstName,
138             LastName = result.LastName,
139             PhoneNo = result.PhoneNo,
140             CardToken = result.CardToken,
141             PublishableKey = result.PublishableKey,
142             HasCreditCard = result.HasCreditCard,
143             PromisePayCardName = result.PromisePayCardName,
144             CardType = result.CardType,
145             ExpiryDate = result.ExpiryDate,
146             CardNumber = result.CardNumber
147         };
148     }
149 
150     private async Task UpdateUser(CarParkUserDetails existingCarParkUser, CancellationToken cancellationToken)
151     {
152         Guard.Against.Null(existingCarParkUser);
153 
154         var updateUserRequest = new UpdateUserRequest
155         {
156             UserID = existingCarParkUser.UserId,
157             Email = _userIdentity.Email,
158             FirstName = _userIdentity.FirstName,
159             LastName = _userIdentity.LastName,
160             PhoneNo = _userIdentity.MobilePhone
161         };
162 
163         var result = await _ubiParkDataAccessService.UpdateUser(updateUserRequest, cancellationToken);
164         if (!result.Success)
165         {
166             var errors = string.Join(',', result.Errors);
167             _logger.LogError("Failed to update user {UserId}. Errors: {Errors}", updateUserRequest.UserID, errors);
168         }
169         else
170         {
171             existingCarParkUser.Email = _userIdentity.Email;
172             existingCarParkUser.FirstName = _userIdentity.FirstName;
173             existingCarParkUser.LastName = _userIdentity.LastName;
174             existingCarParkUser.PhoneNo = _userIdentity.MobilePhone;
175         }
176     }
177 
178     private bool UserInformationHasChanged(CarParkUserDetails existingCarParkUser)
179     {
180         Guard.Against.Null(existingCarParkUser);
181 
182         return existingCarParkUser.Email != _userIdentity.Email ||
183             existingCarParkUser.FirstName != _userIdentity.FirstName ||
184             existingCarParkUser.LastName != _userIdentity.LastName ||
185             existingCarParkUser.PhoneNo != _userIdentity.MobilePhone;
186     }
187 }